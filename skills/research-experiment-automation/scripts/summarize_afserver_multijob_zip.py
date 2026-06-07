#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import statistics
import tempfile
import zipfile
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def infer_offset(name: str, chain_index: int) -> int:
    """Return residue offset for converting local residue IDs to absolute IDs."""
    if chain_index == 0:
        match = re.search(r"_(\d+)_(\d+)(?:\b|_)", name)
        if match:
            return int(match.group(1)) - 1
    if chain_index == 1:
        match = re.search(r"ank[_-](\d+)[_-](\d+)", name, flags=re.IGNORECASE)
        if match:
            return int(match.group(1)) - 1
    return 0


def job_object(job_dir: Path) -> dict[str, Any]:
    request_path = next(job_dir.glob("*job_request.json"))
    request = read_json(request_path)
    return request[0] if isinstance(request, list) else request


def chain_sequences(job: dict[str, Any]) -> list[str]:
    seqs = []
    for item in job.get("sequences", []):
        protein = item.get("proteinChain") or item.get("protein") or item
        seqs.append(protein.get("sequence", ""))
    return seqs


def summarize_model(job_dir: Path, full_path: Path, summary_path: Path, job_name: str) -> dict[str, Any]:
    full = read_json(full_path)
    summary = read_json(summary_path)

    token_chains = full["token_chain_ids"]
    token_res_ids = full["token_res_ids"]
    idx_a = [i for i, chain in enumerate(token_chains) if chain == "A"]
    idx_b = [i for i, chain in enumerate(token_chains) if chain == "B"]

    pae = full["pae"]
    contact = full["contact_probs"]
    inter_pae = [pae[i][j] for i in idx_a for j in idx_b] + [pae[j][i] for i in idx_a for j in idx_b]
    inter_contact = [contact[i][j] for i in idx_a for j in idx_b] + [contact[j][i] for i in idx_a for j in idx_b]

    atom_chains = full["atom_chain_ids"]
    atom_plddt = full["atom_plddts"]
    plddt_a = [score for score, chain in zip(atom_plddt, atom_chains) if chain == "A"]
    plddt_b = [score for score, chain in zip(atom_plddt, atom_chains) if chain == "B"]

    offset_a = infer_offset(job_name, 0)
    offset_b = infer_offset(job_name, 1)
    pairs = []
    for i in idx_a:
        for j in idx_b:
            pairs.append(
                {
                    "chain_a_residue": token_res_ids[i],
                    "chain_b_residue": token_res_ids[j],
                    "chain_a_absolute_residue": token_res_ids[i] + offset_a,
                    "chain_b_absolute_residue": token_res_ids[j] + offset_b,
                    "pae": pae[i][j],
                    "contact_probability": contact[i][j],
                }
            )

    model_match = re.search(r"_(\d+)\.json$", full_path.name)
    model_index = int(model_match.group(1)) if model_match else -1

    return {
        "model": model_index,
        "ranking_score": summary.get("ranking_score"),
        "iptm": summary.get("iptm"),
        "ptm": summary.get("ptm"),
        "chain_pair_iptm_ab": (summary.get("chain_pair_iptm") or [[None, None], [None, None]])[0][1],
        "chain_pair_pae_min_ab": (summary.get("chain_pair_pae_min") or [[None, None], [None, None]])[0][1],
        "mean_inter_chain_pae": statistics.mean(inter_pae),
        "min_inter_chain_pae": min(inter_pae),
        "mean_contact_probability": statistics.mean(inter_contact),
        "max_contact_probability": max(inter_contact),
        "chain_a_mean_plddt": statistics.mean(plddt_a) if plddt_a else None,
        "chain_b_mean_plddt": statistics.mean(plddt_b) if plddt_b else None,
        "low_pae_pairs": sorted(pairs, key=lambda row: (row["pae"], -row["contact_probability"]))[:10],
        "top_contact_pairs": sorted(pairs, key=lambda row: row["contact_probability"], reverse=True)[:10],
    }


def summarize_root(root: Path) -> dict[str, Any]:
    jobs = []
    for job_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        if not list(job_dir.glob("*job_request.json")):
            continue
        job = job_object(job_dir)
        job_name = job.get("name") or job_dir.name
        seqs = chain_sequences(job)
        models = []
        for full_path in sorted(job_dir.glob("*full_data_*.json")):
            summary_path = job_dir / full_path.name.replace("full_data", "summary_confidences")
            if summary_path.exists():
                models.append(summarize_model(job_dir, full_path, summary_path, job_name))
        models.sort(key=lambda row: row["ranking_score"] if row["ranking_score"] is not None else -1, reverse=True)
        jobs.append(
            {
                "directory": job_dir.name,
                "name": job_name,
                "chain_lengths": [len(seq) for seq in seqs],
                "chain_starts": [seq[:20] for seq in seqs],
                "models": models,
                "best_model": models[0] if models else None,
            }
        )
    return {"jobs": jobs}


def format_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# AlphaFold Server multi-job summary",
        "",
        "| Job | Chain lengths | Best model | ranking_score | ipTM | pTM | mean inter-chain PAE | min inter-chain PAE | max contact | pLDDT A/B |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for job in summary["jobs"]:
        best = job["best_model"]
        if not best:
            continue
        lines.append(
            "| {name} | {lengths} | model {model} | {ranking:.3f} | {iptm:.3f} | {ptm:.3f} | {mean_pae:.2f} | {min_pae:.2f} | {max_contact:.3f} | {plddt_a:.1f}/{plddt_b:.1f} |".format(
                name=job["name"],
                lengths="/".join(str(x) for x in job["chain_lengths"]),
                model=best["model"],
                ranking=best["ranking_score"],
                iptm=best["iptm"],
                ptm=best["ptm"],
                mean_pae=best["mean_inter_chain_pae"],
                min_pae=best["min_inter_chain_pae"],
                max_contact=best["max_contact_probability"],
                plddt_a=best["chain_a_mean_plddt"],
                plddt_b=best["chain_b_mean_plddt"],
            )
        )

    lines.extend(["", "## Best-model hotspot candidates", ""])
    for job in summary["jobs"]:
        best = job["best_model"]
        if not best:
            continue
        lines.extend([f"### {job['name']}", ""])
        for pair in best["low_pae_pairs"][:8]:
            lines.append(
                "- A{a}/abs{aa} - B{b}/abs{bb}: PAE={pae:.1f}, contact={contact:.3f}".format(
                    a=pair["chain_a_residue"],
                    aa=pair["chain_a_absolute_residue"],
                    b=pair["chain_b_residue"],
                    bb=pair["chain_b_absolute_residue"],
                    pae=pair["pae"],
                    contact=pair["contact_probability"],
                )
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize multi-job AlphaFold Server result ZIPs by job.")
    parser.add_argument("input", help="AlphaFold Server result zip or extracted result directory")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--out", help="Output file path; defaults to stdout")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    temp_dir = None
    try:
        root = input_path
        if input_path.is_file() and input_path.suffix.lower() == ".zip":
            temp_dir = tempfile.TemporaryDirectory()
            root = Path(temp_dir.name)
            with zipfile.ZipFile(input_path) as zf:
                zf.extractall(root)

        summary = summarize_root(root)
        rendered = json.dumps(summary, ensure_ascii=False, indent=2) if args.format == "json" else format_markdown(summary)

        if args.out:
            Path(args.out).expanduser().write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
