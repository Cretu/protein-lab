#!/usr/bin/env python3
"""Audit and conservatively parse Tamarind PepMLM result packages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


AA_RE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYXBZUOJ]+$")
STRICT_AA_RE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWY]+$")
TEXT_EXTENSIONS = {".csv", ".tsv", ".txt", ".json", ".jsonl", ".out", ".log", ".md"}
TEXT_SIZE_LIMIT_BYTES = 10_000_000
SEQUENCE_KEY_HINTS = ("peptide", "binder", "design", "sequence", "seq")
TARGET_KEY_HINTS = ("target", "protein", "receptor")
RANK_KEY_HINTS = ("rank", "order", "index", "idx")
SCORE_KEY_HINTS = ("score", "prob", "confidence", "reward", "loss", "affinity", "rank")


@dataclass
class TextFile:
    path: str
    data: bytes
    size: int
    sha256: str


@dataclass
class Candidate:
    sequence: str
    source_file: str
    source_format: str
    source_row: str
    source_column: str
    source_order: int
    fields: dict[str, Any] = field(default_factory=dict)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def iter_package_files(path: Path) -> tuple[list[dict[str, Any]], list[TextFile]]:
    inventory: list[dict[str, Any]] = []
    text_files: list[TextFile] = []

    def add_file(name: str, data: bytes) -> None:
        suffix = Path(name).suffix.lower()
        digest = sha256(data)
        if suffix in TEXT_EXTENSIONS:
            kind = "text" if len(data) <= TEXT_SIZE_LIMIT_BYTES else "text-too-large"
        else:
            kind = "binary-or-unknown"
        inventory.append({"path": name, "size": len(data), "sha256": digest, "kind": kind})
        if kind == "text":
            text_files.append(TextFile(name, data, len(data), digest))

    if path.is_dir():
        for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
            add_file(str(file_path.relative_to(path)), file_path.read_bytes())
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            for info in sorted(zf.infolist(), key=lambda item: item.filename):
                if info.is_dir():
                    continue
                add_file(info.filename, zf.read(info))
    elif path.is_file():
        add_file(path.name, path.read_bytes())
    else:
        raise FileNotFoundError(path)
    return inventory, text_files


def decode_text(file: TextFile) -> str | None:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return file.data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def normalize_sequence(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "")).upper()


def sequence_ok(sequence: str, expected_length: int | None) -> bool:
    if not sequence or not AA_RE.fullmatch(sequence):
        return False
    if expected_length is not None:
        return len(sequence) == expected_length
    return 4 <= len(sequence) <= 80


def key_has_any(key: str, hints: Iterable[str]) -> bool:
    lowered = re.sub(r"[^a-z0-9]+", "", key.lower())
    return any(hint in lowered for hint in hints)


def is_candidate_key(key: str) -> bool:
    return key_has_any(key, SEQUENCE_KEY_HINTS) and not key_has_any(key, TARGET_KEY_HINTS)


def score_fields(row: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for key, value in row.items():
        if key_has_any(str(key), SCORE_KEY_HINTS):
            fields[str(key)] = value
    return fields


def parse_number(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(str(value).strip())
    except ValueError:
        return None


def row_rank_value(candidate: Candidate) -> float | None:
    for key, value in candidate.fields.items():
        if key_has_any(key, RANK_KEY_HINTS):
            number = parse_number(value)
            if number is not None:
                return number
    return None


def csv_dialect(text: str, suffix: str) -> csv.Dialect:
    if suffix == ".tsv":
        return csv.excel_tab
    try:
        return csv.Sniffer().sniff(text[:4096], delimiters=",\t;")
    except csv.Error:
        return csv.excel


def parse_table(file: TextFile, text: str, expected_length: int | None, order_start: int) -> list[Candidate]:
    candidates: list[Candidate] = []
    stream = io.StringIO(text)
    try:
        reader = csv.DictReader(stream, dialect=csv_dialect(text, Path(file.path).suffix.lower()))
    except csv.Error:
        return candidates
    if not reader.fieldnames:
        return candidates
    candidate_columns = [name for name in reader.fieldnames if name and is_candidate_key(name)]
    if not candidate_columns:
        return candidates
    for row_index, row in enumerate(reader, start=1):
        for column in candidate_columns:
            sequence = normalize_sequence(row.get(column))
            if sequence_ok(sequence, expected_length):
                candidates.append(
                    Candidate(
                        sequence=sequence,
                        source_file=file.path,
                        source_format="table",
                        source_row=str(row_index),
                        source_column=column,
                        source_order=order_start + len(candidates),
                        fields=score_fields(row),
                    )
                )
                break
    return candidates


def parse_json_value(
    file: TextFile,
    value: Any,
    expected_length: int | None,
    order_start: int,
    format_name: str,
) -> list[Candidate]:
    candidates: list[Candidate] = []

    def visit(child: Any, json_path: str) -> None:
        if isinstance(child, dict):
            for key, raw in child.items():
                if not is_candidate_key(str(key)):
                    continue
                sequence = normalize_sequence(raw)
                if sequence_ok(sequence, expected_length):
                    candidates.append(
                        Candidate(
                            sequence,
                            file.path,
                            format_name,
                            json_path or "$",
                            str(key),
                            order_start + len(candidates),
                            score_fields(child),
                        )
                    )
                    break
            for key, nested in child.items():
                nested_path = f"{json_path}.{key}" if json_path else str(key)
                visit(nested, nested_path)
        elif isinstance(child, list):
            for idx, nested in enumerate(child):
                visit(nested, f"{json_path}[{idx}]")
        elif isinstance(child, str):
            leaf_key = json_path.split(".")[-1].split("[")[0]
            sequence = normalize_sequence(child)
            if is_candidate_key(leaf_key) and sequence_ok(sequence, expected_length):
                candidates.append(
                    Candidate(sequence, file.path, format_name, json_path, leaf_key, order_start + len(candidates), {})
                )

    visit(value, "")
    return candidates


def parse_json_file(file: TextFile, text: str, expected_length: int | None, order_start: int) -> list[Candidate]:
    suffix = Path(file.path).suffix.lower()
    candidates: list[Candidate] = []
    if suffix == ".jsonl":
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            for cand in parse_json_value(file, value, expected_length, order_start + len(candidates), "jsonl"):
                cand.source_row = f"line {line_no}:{cand.source_row}"
                candidates.append(cand)
        return candidates
    try:
        return parse_json_value(file, json.loads(text), expected_length, order_start, "json")
    except json.JSONDecodeError:
        return []


def parse_text(file: TextFile, text: str, expected_length: int | None, order_start: int) -> list[Candidate]:
    candidates: list[Candidate] = []
    # Anchor with negative lookarounds so longer uppercase tokens (e.g. headers
    # or accession-like IDs) are not silently truncated to the first N residues.
    core = r"[ACDEFGHIKLMNPQRSTVWYXBZUOJ]"
    length_clause = f"{{{expected_length}}}" if expected_length else "{4,80}"
    pattern = rf"(?<![A-Z]){core}{length_clause}(?![A-Z])"
    seen_in_file: set[str] = set()
    for line_no, line in enumerate(text.splitlines(), start=1):
        if key_has_any(line, TARGET_KEY_HINTS):
            continue
        for match in re.finditer(pattern, line.upper()):
            sequence = match.group(0)
            if sequence in seen_in_file or not sequence_ok(sequence, expected_length):
                continue
            seen_in_file.add(sequence)
            candidates.append(
                Candidate(sequence, file.path, "text", f"line {line_no}", "regex", order_start + len(candidates), {})
            )
    return candidates


def parse_candidates(text_files: list[TextFile], expected_length: int | None) -> list[Candidate]:
    candidates: list[Candidate] = []
    for file in text_files:
        text = decode_text(file)
        if text is None:
            continue
        suffix = Path(file.path).suffix.lower()
        parsed: list[Candidate] = []
        if suffix in {".csv", ".tsv"}:
            parsed = parse_table(file, text, expected_length, len(candidates))
        elif suffix in {".json", ".jsonl"}:
            parsed = parse_json_file(file, text, expected_length, len(candidates))
        elif suffix in {".txt", ".out", ".log", ".md"}:
            # Regex-only fallback is reserved for free-text formats. Tabular
            # files with no recognizable candidate column are surfaced via
            # inventory + interpretation, not mined with a permissive regex
            # that can pick target sequences out of comments or headers.
            parsed = parse_text(file, text, expected_length, len(candidates))
        candidates.extend(parsed)
    return candidates


def issue_flags(sequence: str, expected_length: int | None) -> list[str]:
    flags: list[str] = []
    if expected_length is not None and len(sequence) != expected_length:
        flags.append("length-mismatch")
    if not STRICT_AA_RE.fullmatch(sequence):
        flags.append("noncanonical-aa")
    if re.search(r"(.)\1\1\1", sequence):
        flags.append("homopolymer-run")
    if re.search(r"N[^P][ST]", sequence):
        flags.append("n-glyco-motif")
    if sequence.count("C") >= 3:
        flags.append("high-cysteine")
    if "CC" in sequence:
        flags.append("adjacent-cysteine")
    return flags


def compact_fields(fields: dict[str, Any]) -> str:
    if not fields:
        return ""
    parts = []
    for key in sorted(fields):
        value = fields[key]
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False, sort_keys=True)
        parts.append(f"{key}={value}")
    return "; ".join(parts)


def dedupe_candidates(candidates: list[Candidate], expected_length: int | None) -> list[dict[str, Any]]:
    grouped: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.sequence, []).append(candidate)
    rows: list[dict[str, Any]] = []
    for sequence, group in grouped.items():
        ranked = [(row_rank_value(cand), cand) for cand in group]
        _, best = min(ranked, key=lambda item: (item[0] is None, item[0] or 0, item[1].source_order))
        rows.append(
            {
                "sequence": sequence,
                "length": len(sequence),
                "expected_length_match": expected_length is None or len(sequence) == expected_length,
                "duplicate_count": len(group),
                "source_files": ",".join(sorted({cand.source_file for cand in group})),
                "source_format": best.source_format,
                "source_row": best.source_row,
                "source_column": best.source_column,
                "source_order": best.source_order,
                "source_rank": row_rank_value(best),
                "score_fields": compact_fields(best.fields),
                "issue_flags": ",".join(issue_flags(sequence, expected_length)),
            }
        )
    rows.sort(key=lambda row: (row["source_rank"] is None, row["source_rank"] or 0, row["source_order"], row["sequence"]))
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx
    return rows


def write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def interpretation_text(
    source: Path,
    inventory: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    top_n: int,
    expected_length: int | None,
) -> str:
    lines = [
        "# PepMLM Result Interpretation (draft)",
        "",
        "> Draft generated by inspect_pepmlm_result.py. Localize and tighten",
        "> conclusions through the `reporting` skill before sharing.",
        "",
        "## One-line Conclusion",
    ]
    if rows:
        lines.append(
            f"Identified {len(rows)} deduplicated PepMLM candidate peptides. Treat the ranking as generator priority only, "
            "not as proof of binding, degradation, or mechanism."
        )
    else:
        lines.append(
            "Raw audit completed but no parseable candidate table was identified; do not produce a shortlist yet."
        )
    lines.extend(
        [
            "",
            "## Raw Evidence",
            f"- Source: `{source}`",
            f"- Raw files inventoried: {len(inventory)}",
            f"- Expected peptide length: {expected_length if expected_length is not None else 'not specified'}",
            "",
            "## Candidate Shortlist",
        ]
    )
    if rows:
        for row in rows[:top_n]:
            flags = row["issue_flags"] or "none"
            score = row["score_fields"] or "not detected"
            lines.append(f"- #{row['rank']} `{row['sequence']}` length={row['length']} flags={flags}; scores={score}")
    else:
        lines.append("- No candidate sequences were extracted. Review `pepmlm_result_inventory.tsv` and raw files manually.")
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "- PepMLM rank or score is a generator signal, not an experimentally validated binding or degradation measurement.",
            "- Do not infer target patch, binding pose, interface confidence, or GRK4 degradation from PepMLM alone.",
            "- Candidates should be validated with AF Server or wet-lab experiments before being described as stronger binders.",
            "",
            "## Suggested Next Step",
        ]
    )
    if rows:
        clean = [row for row in rows if not row["issue_flags"]]
        pool = clean or rows
        selected = ", ".join(f"`{row['sequence']}`" for row in pool[: min(top_n, 8)])
        lines.append(f"- Build an AF Server validation panel from: {selected}.")
        lines.append("- Include parent or benchmark peptide plus scrambled/negative control when moving to experiment design.")
    else:
        lines.append("- Re-open the raw result package or download the job again; do not proceed to shortlist until candidates are extracted.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="PepMLM result zip, folder, or file.")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--expected-length", type=int)
    parser.add_argument("--top-n", type=int, default=12)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    try:
        inventory, text_files = iter_package_files(args.source)
        raw_candidates = parse_candidates(text_files, args.expected_length)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    rows = dedupe_candidates(raw_candidates, args.expected_length)
    inventory_path = args.out_dir / "pepmlm_result_inventory.tsv"
    candidate_path = args.out_dir / "pepmlm_candidates.tsv"
    summary_path = args.out_dir / "pepmlm_inspection_summary.json"
    interpretation_path = args.out_dir / "pepmlm_interpretation.md"

    write_tsv(inventory_path, inventory, ["path", "size", "sha256", "kind"])
    candidate_fields = [
        "rank",
        "sequence",
        "length",
        "expected_length_match",
        "duplicate_count",
        "source_files",
        "source_format",
        "source_row",
        "source_column",
        "source_order",
        "source_rank",
        "score_fields",
        "issue_flags",
    ]
    write_tsv(candidate_path, rows, candidate_fields)
    summary = {
        "source": str(args.source),
        "raw_file_count": len(inventory),
        "text_file_count": len(text_files),
        "raw_candidate_mentions": len(raw_candidates),
        "candidate_count": len(rows),
        "expected_length": args.expected_length,
        "outputs": {
            "inventory": str(inventory_path),
            "candidates": str(candidate_path),
            "summary": str(summary_path),
            "interpretation": str(interpretation_path),
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    interpretation_path.write_text(
        interpretation_text(args.source, inventory, rows, args.top_n, args.expected_length),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
