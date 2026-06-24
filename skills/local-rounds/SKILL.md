---
name: local-rounds
description: "Use for Protein Lab local project workspaces and experiment round folders: selecting or using the current directory, creating stable round directories, initializing plan/status_log skeletons, organizing inputs, raw outputs, parsed outputs, reports, auth_pending files, and traceability links."
---

# Local Rounds

Use this skill for local project workspaces, experiment round folders, and file hygiene. It does not design experiments, run tools, interpret results, post to Feishu, or write final reports.

## Core Responsibility

- Create or find the active local project workspace and round directory.
- Keep files named consistently and stored in the right place.
- Maintain `status_log.md` as the run ledger.
- Preserve traceability between source inputs, tool outputs, reports, and collaboration links.

## Root And Naming

Resolve the workspace root in this order:

1. explicit user path or `--root`
2. nearest `.protein-lab/project.json` found from the current directory upward
3. current Codex project/current directory
4. `~/.config/protein-lab/config.json` `workspace_root`
5. `${PROTEIN_LAB_ROOT}`
6. `~/Documents/Protein Lab`

Prefer the nearest project-local config when it exists. Prefer the current directory when the user opened Codex inside a new project and wants to initialize Protein Lab there. Use `setup` when the workspace choice is unclear or should be written into local config.

## Isolation Rules

- Treat each configured workspace root as a separate project.
- Keep rounds, raw outputs, parsed outputs, reports, wiki roots, and Feishu links inside or attached to that project unless the user explicitly asks for a shared team location.
- Do not infer one project's active round from another project's `status_log.md`.
- If multiple projects are open, identify the workspace root before creating or updating files.

Prefer stable, ASCII-friendly directory names:

```text
GRK4_C650_peptide_vs_ZDHHC17_ANK11-305/
EVTCGL_repeat_vs_ZDHHC17_ANK11-305/
GRK4_Cterm450-578_vs_ZDHHC17_full_and_ANK11-305/
```

Good names include the main molecule or construct, comparison target, and scope. Avoid date-only or vague names such as `test1/` or `new_round/`.

## Standard Round Contents

- `<slug>_plan.md`
- `inputs/`
- `outputs/raw/`
- `outputs/parsed/`
- `reports/`
- `<slug>.fasta` when sequence review is useful
- tool input files such as `<slug>_afserver.json`
- Tamarind payloads such as `<slug>_pepmlm_payload.json`
- manifest or comparison table when there are multiple jobs
- raw outputs such as `folds_<slug>_afserver.zip`
- Tamarind raw outputs such as `<jobName>_pepmlm_raw.zip`
- tool inspection outputs such as `pepmlm_result_inventory.tsv`, `pepmlm_candidates.tsv`, and `pepmlm_interpretation.md`
- generated audit directories
- final reports or summaries
- `status_log.md`
- `auth_pending.json` only when external authorization is pending

## Initialization Script

Use the bundled script for a basic skeleton:

```bash
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/local-rounds/scripts/init_round.py" --title "<任务标题>"
# Defaults to the current directory as the workspace.
# Override the root: --root "/custom/path"
# Ignore current directory and use config/env/default: --no-cwd
```

The script creates the round directory, `inputs/`, `outputs/raw/`, `outputs/parsed/`, `reports/`, a plan file, and `status_log.md`. Fill scientific content through `experiment`, tool-specific details through the relevant `tool-*` skill, and final wording through `reporting`.

## Status Log Rules

Record:

- source request and collaboration links, if any
- exact input source, accession, sequence length, construct boundary, and file path
- tool name, parameters, seed when relevant, job ID or job name, submission time, and queue state
- download path, file size, and raw output checksum when useful
- parsed candidate table path and interpretation path when a tool-specific parser was used
- blocker, authorization state, user handoff, and retry decision
- final report path and postmortem guardrails

If an online step fails, preserve the current local inputs and status before retrying.
