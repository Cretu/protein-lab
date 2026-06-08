#!/usr/bin/env python3
"""Audit AlphaFold Server result zips or extracted directories.

The script is intentionally lightweight: it inventories jobs, pairs raw
summary/full_data JSON files, calculates common two-chain interface metrics,
and emits JSON plus Markdown for human interpretation.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import tempfile
import zipfile
from pathlib import Path
from typing import Any


MODEL_RE = re.compile(r"_(?:summary_confidences|full_data)_(\d+)\.json$")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def model_index(path: Path) -> int | None:
    match = MODEL_RE.search(path.name)
    return int(match.group(1)) if match else None


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def source_root(path: Path, temp_root: Path) -> Path:
    if path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            archive.extractall(temp_root)
        return temp_root
    if path.is_dir():
        return path
    raise FileNotFoundError(f"Input is not an AF Server zip or directory: {path}")


def find_job_dirs(root: Path) -> list[Path]:
    dirs = {
        path.parent
        for path in root.rglob("*_summary_confidences_*.json")
        if path.is_file()
    }
    return sorted(dirs, key=lambda path: str(path.relative_to(root)))


def find_request(job_dir: Path) -> dict[str, Any] | None:
    request_paths = sorted(job_dir.glob("*job_request.json"))
    if not request_paths:
        return None
    request = read_json(request_paths[0])
    if isinstance(request, list) and request:
        return request[0]
    if isinstance(request, dict):
        return request
    return None


def plddt_by_chain(full: dict[str, Any]) -> dict[str, float | None]:
    atom_chains = full.get("atom_chain_ids") or []
    atom_plddts = full.get("atom_plddts") or []
    result: dict[str, float | None] = {}
    for chain in ordered_unique(atom_chains):
        values = [
            float(score)
            for score, atom_chain in zip(atom_plddts, atom_chains)
            if atom_chain == chain
        ]
        result[chain] = mean(values)
    return result


def summarize_pair(full: dict[str, Any]) -> dict[str, Any]:
    token_chains = full.get("token_chain_ids") or []
    token_res_ids = full.get("token_res_ids") or list(range(1, len(token_chains) + 1))
    chains = ordered_unique(token_chains)
    if len(chains) < 2:
        return {"chains": chains, "warning": "fewer_than_two_token_chains"}

    chain_a, chain_b = chains[0], chains[1]
    idx_a = [idx for idx, chain in enumerate(token_chains) if chain == chain_a]
    idx_b = [idx for idx, chain in enumerate(token_chains) if chain == chain_b]
    pae = full.get("pae") or []
    contact = full.get("contact_probs") or []

    inter_pae: list[float] = []
    inter_contact: list[float] = []
    pairs: list[dict[str, Any]] = []
    for i in idx_a:
        for j in idx_b:
            try:
                pae_ab = float(pae[i][j])
                pae_ba = float(pae[j][i])
                contact_ab = float(contact[i][j])
                contact_ba = float(contact[j][i])
            except Exception:
                continue
            pae_mean = (pae_ab + pae_ba) / 2
            contact_mean = (contact_ab + contact_ba) / 2
            inter_pae.extend([pae_ab, pae_ba])
            inter_contact.extend([contact_ab, contact_ba])
            pairs.append(
                {
                    "chain_a": chain_a,
                    "chain_a_residue": token_res_ids[i],
                    "chain_b": chain_b,
                    "chain_b_residue": token_res_ids[j],
                    "pae_mean": pae_mean,
                    "contact_mean": contact_mean,
                    "pae_ab": pae_ab,
                    "pae_ba": pae_ba,
                    "contact_ab": contact_ab,
                    "contact_ba": contact_ba,
                }
            )

    top_contacts = sorted(
        pairs,
        key=lambda item: (item["contact_mean"], -item["pae_mean"]),
        reverse=True,
    )[:20]
    low_pae = sorted(
        pairs,
        key=lambda item: (item["pae_mean"], -item["contact_mean"]),
    )[:20]

    return {
        "chains": chains,
        "primary_pair": [chain_a, chain_b],
        "mean_inter_chain_pae": mean(inter_pae),
        "min_inter_chain_pae": min(inter_pae) if inter_pae else None,
        "max_contact_probability": max(inter_contact) if inter_contact else None,
        "mean_contact_probability": mean(inter_contact),
        "low_pae_pair_count_lt_10": sum(1 for item in pairs if item["pae_mean"] < 10),
        "low_pae_pair_count_lt_15": sum(1 for item in pairs if item["pae_mean"] < 15),
        "contact_pair_count_ge_0_20": sum(1 for item in pairs if item["contact_mean"] >= 0.20),
        "contact_pair_count_ge_0_50": sum(1 for item in pairs if item["contact_mean"] >= 0.50),
        "top_contacts": top_contacts,
        "low_pae_pairs": low_pae,
    }


def summarize_model(summary_path: Path, full_path: Path | None) -> dict[str, Any]:
    summary = read_json(summary_path)
    row: dict[str, Any] = {
        "model": model_index(summary_path),
        "summary_path": str(summary_path),
        "full_data_path": str(full_path) if full_path else None,
        "ranking_score": summary.get("ranking_score"),
        "iptm": summary.get("iptm"),
        "ptm": summary.get("ptm"),
        "chain_pair_iptm": summary.get("chain_pair_iptm"),
        "chain_pair_pae_min": summary.get("chain_pair_pae_min"),
        "fraction_disordered": summary.get("fraction_disordered"),
        "has_clash": summary.get("has_clash"),
    }
    if full_path is None:
        row["warning"] = "missing_full_data_json"
        return row

    full = read_json(full_path)
    row["chain_mean_plddt"] = plddt_by_chain(full)
    row.update(summarize_pair(full))
    return row


def summarize_job(root: Path, job_dir: Path) -> dict[str, Any]:
    request = find_request(job_dir)
    summary_paths = sorted(job_dir.glob("*_summary_confidences_*.json"), key=lambda p: model_index(p) or -1)
    full_by_index = {
        model_index(path): path
        for path in job_dir.glob("*_full_data_*.json")
        if model_index(path) is not None
    }

    models = [
        summarize_model(path, full_by_index.get(model_index(path)))
        for path in summary_paths
    ]
    models.sort(
        key=lambda row: (
            row.get("ranking_score") if row.get("ranking_score") is not None else -1,
            row.get("iptm") if row.get("iptm") is not None else -1,
        ),
        reverse=True,
    )

    warnings: list[str] = []
    if not request:
        warnings.append("missing_job_request_json")
    if len(summary_paths) != len(full_by_index):
        warnings.append("summary_full_data_count_mismatch")

    return {
        "job_dir": str(job_dir.relative_to(root)),
        "job_name": request.get("name") if request else job_dir.name,
        "seed": (request.get("modelSeeds") or [None])[0] if request else None,
        "model_count": len(models),
        "warnings": warnings,
        "models": models,
        "best_model": models[0] if models else None,
    }


def audit(path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        root = source_root(path.resolve(), tmp_root)
        jobs = [summarize_job(root, job_dir) for job_dir in find_job_dirs(root)]
        warnings: list[str] = []
        if not jobs:
            warnings.append("no_raw_summary_confidences_json_found")
        if len(jobs) > 1:
            warnings.append("multi_job_package_split_before_comparing")

        return {
            "source": str(path.resolve()),
            "job_count": len(jobs),
            "warnings": warnings,
            "jobs": jobs,
        }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# AF Server Audit",
        "",
        f"- Source: `{summary['source']}`",
        f"- Jobs found: {summary['job_count']}",
    ]
    if summary["warnings"]:
        lines.append("- Warnings: " + ", ".join(summary["warnings"]))
    lines.extend(
        [
            "",
            "## Job Summary",
            "",
            "| Job | Models | Best model | ranking | ipTM | pTM | mean inter-PAE | min inter-PAE | max contact | chain pLDDT | warnings |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for job in summary["jobs"]:
        best = job.get("best_model") or {}
        plddt = best.get("chain_mean_plddt") or {}
        plddt_text = ", ".join(f"{chain}:{fmt(value, 1)}" for chain, value in plddt.items())
        lines.append(
            "| {job} | {models} | {model} | {ranking} | {iptm} | {ptm} | {mean_pae} | {min_pae} | {contact} | {plddt} | {warnings} |".format(
                job=job.get("job_name") or job.get("job_dir"),
                models=job.get("model_count"),
                model=fmt(best.get("model")),
                ranking=fmt(best.get("ranking_score")),
                iptm=fmt(best.get("iptm")),
                ptm=fmt(best.get("ptm")),
                mean_pae=fmt(best.get("mean_inter_chain_pae"), 2),
                min_pae=fmt(best.get("min_inter_chain_pae"), 2),
                contact=fmt(best.get("max_contact_probability"), 3),
                plddt=plddt_text,
                warnings=", ".join(job.get("warnings") or []),
            )
        )

    lines.extend(["", "## Best-model Top Contacts", ""])
    for job in summary["jobs"]:
        best = job.get("best_model") or {}
        top_contacts = best.get("top_contacts") or []
        lines.append(f"### {job.get('job_name') or job.get('job_dir')}")
        if not top_contacts:
            lines.append("")
            lines.append("- No contact pairs available.")
            lines.append("")
            continue
        lines.extend(
            [
                "",
                "| A residue | B residue | contact | PAE |",
                "|---:|---:|---:|---:|",
            ]
        )
        for item in top_contacts[:10]:
            lines.append(
                "| {a} | {b} | {contact} | {pae} |".format(
                    a=item["chain_a_residue"],
                    b=item["chain_b_residue"],
                    contact=fmt(item["contact_mean"], 3),
                    pae=fmt(item["pae_mean"], 2),
                )
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="AF Server zip or extracted result directory")
    parser.add_argument("--out-dir", default="", help="Directory for afserver_audit.json and afserver_audit.md")
    args = parser.parse_args()

    summary = audit(Path(args.input))
    if args.out_dir:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "afserver_audit.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (out_dir / "afserver_audit.md").write_text(render_markdown(summary), encoding="utf-8")
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
