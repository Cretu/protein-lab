---
name: local-rounds
description: "Use for Protein Lab local experiment round folders: creating stable round directories, naming files, initializing plan/status_log skeletons, organizing FASTA/JSON inputs, raw tool outputs, reports, auth_pending files, and traceability links under /Users/luke/Documents/Protein Lab."
---

# Local Rounds

Use this skill for local experiment folders and file hygiene. It does not design experiments, run tools, interpret results, post to Feishu, or write final reports.

## Core Responsibility

- Create or find the active local round directory.
- Keep files named consistently and stored in the right place.
- Maintain `status_log.md` as the run ledger.
- Preserve traceability between source inputs, tool outputs, reports, and collaboration links.

## Root And Naming

Use `/Users/luke/Documents/Protein Lab` unless the user gives another path.

Prefer stable, ASCII-friendly directory names:

```text
GRK4_C650_peptide_vs_ZDHHC17_ANK11-305/
EVTCGL_repeat_vs_ZDHHC17_ANK11-305/
GRK4_Cterm450-578_vs_ZDHHC17_full_and_ANK11-305/
```

Good names include the main molecule or construct, comparison target, and scope. Avoid date-only or vague names such as `test1/` or `new_round/`.

## Standard Round Contents

- `<slug>_plan.md`
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
python3 /Users/luke/plugins/protein-lab/skills/local-rounds/scripts/init_round.py --title "<任务标题>" --root "/Users/luke/Documents/Protein Lab"
```

The script creates the directory, a plan file, and `status_log.md`. Fill scientific content through `experiment`, tool-specific details through the relevant `tool-*` skill, and final wording through `reporting`.

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
