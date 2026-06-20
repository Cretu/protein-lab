#!/usr/bin/env python3
"""Prepare a Tamarind PepMLM submit-job payload."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


JOB_RE = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
NUM_DESIGNS = {"1", "2", "4", "8", "16", "32"}


class PayloadError(RuntimeError):
    pass


def read_sequence(path: Path | None, inline: str | None) -> str:
    if path and inline:
        raise PayloadError("Use either --input or --sequence, not both.")
    if not path and not inline:
        raise PayloadError("One of --input or --sequence is required.")
    text = path.read_text(encoding="utf-8") if path else inline or ""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(">"):
            continue
        lines.append(stripped)
    sequence = re.sub(r"\s+", "", "".join(lines)).upper()
    if not sequence:
        raise PayloadError("Target sequence is empty.")
    if not re.fullmatch(r"[A-Z]+", sequence):
        raise PayloadError("Target sequence must contain amino-acid letters only.")
    return sequence


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    if not JOB_RE.fullmatch(args.job_name):
        raise PayloadError("jobName must be 1-100 chars: letters, digits, underscore, or hyphen.")
    if args.peptide_length < 1:
        raise PayloadError("peptideLength must be positive.")
    num_designs = str(args.num_designs)
    if num_designs not in NUM_DESIGNS:
        raise PayloadError(f"numDesigns must be one of {sorted(NUM_DESIGNS)}.")

    sequence = read_sequence(args.input, args.sequence)
    payload: dict[str, object] = {
        "jobName": args.job_name,
        "type": "pepmlm",
        "settings": {
            "targetSequence": sequence,
            "peptideLength": args.peptide_length,
            "numDesigns": num_designs,
        },
    }
    if args.project_tag:
        payload["projectTag"] = args.project_tag
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="FASTA or plain sequence file.")
    parser.add_argument("--sequence", help="Inline target sequence.")
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--peptide-length", type=int, default=15)
    parser.add_argument("--num-designs", default="8")
    parser.add_argument("--project-tag")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    try:
        payload = build_payload(args)
    except PayloadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    settings = payload["settings"]
    assert isinstance(settings, dict)
    print(
        json.dumps(
            {
                "out": str(args.out),
                "jobName": payload["jobName"],
                "type": payload["type"],
                "targetLength": len(str(settings["targetSequence"])),
                "peptideLength": settings["peptideLength"],
                "numDesigns": settings["numDesigns"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
