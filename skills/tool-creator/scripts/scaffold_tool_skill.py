#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


VALID_KINDS = {"api", "cli", "web", "compute"}


def normalize_tool_name(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        raise ValueError("tool name is empty")
    if not slug.startswith("tool-"):
        slug = f"tool-{slug}"
    if len(slug) > 64:
        raise ValueError("tool skill name must be <= 64 characters")
    return slug


def render_skill(tool_name: str, tool_kind: str, display_name: str) -> str:
    return f"""---
name: {tool_name}
description: "Use for Protein Lab {display_name} work: {tool_kind} preflight, input preparation, run/submit/poll/download flow, raw output audit, conservative interpretation, and handoff to local-rounds, experiment, knowledge-base, or reporting."
---

# {display_name}

Use this skill for {display_name} as a Protein Lab {tool_kind} tool. Replace scaffold notes with facts from primary documentation and a real smoke test before production use.

## When To Use

- The user asks to use {display_name}.
- A Protein Lab task needs {display_name} inputs, execution, result download, result audit, or interpretation.
- A previous manual {display_name} flow should be repeated safely.

## Preflight

- Confirm the local workspace through `setup` and `local-rounds`.
- Check tool availability, account/login state, quotas, and network access.
- Do not transmit private data, credentials, payment details, or irreversible submissions without explicit user authorization.

## Inputs

- Store reviewed inputs in the active local round.
- Record source, version, accession, sequence length, parameters, and intended output.
- Reject or pause on ambiguous inputs instead of guessing.

## Run Flow

- Start with the smallest safe smoke test.
- Capture job IDs, URLs, command versions, request payloads, and raw outputs.
- For long jobs, poll or checkpoint status and update `status_log.md`.

## Result Audit

- Inventory raw outputs before interpretation.
- Identify known result tables/files and surface unknown structures instead of inventing fields.
- Keep generated summaries separate from raw evidence.

## Interpretation Boundary

- Treat tool output as computational evidence only.
- State what the result supports, what it cannot support, and which validation step comes next.

## Handoff

- Use `experiment` for panel decisions and stop/go reasoning.
- Use `knowledge-base` for durable tool lessons.
- Use `reporting` for final Chinese summaries.
"""


def scaffold(skills_root: Path, tool_name: str, tool_kind: str, display_name: str, force: bool = False) -> Path:
    if tool_kind not in VALID_KINDS:
        raise ValueError(f"tool kind must be one of: {', '.join(sorted(VALID_KINDS))}")
    normalized = normalize_tool_name(tool_name)
    skill_dir = skills_root / normalized
    skill_file = skill_dir / "SKILL.md"
    if skill_file.exists() and not force:
        raise FileExistsError(f"{skill_file} already exists; pass --force to overwrite")
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(render_skill(normalized, tool_kind, display_name), encoding="utf-8")
    return skill_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Protein Lab tool-* skill.")
    parser.add_argument("--skills-root", required=True)
    parser.add_argument("--tool-name", required=True)
    parser.add_argument("--tool-kind", choices=sorted(VALID_KINDS), required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    normalized = normalize_tool_name(args.tool_name)
    if args.dry_run:
        print(render_skill(normalized, args.tool_kind, args.display_name))
        return 0
    path = scaffold(Path(args.skills_root), args.tool_name, args.tool_kind, args.display_name, args.force)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
