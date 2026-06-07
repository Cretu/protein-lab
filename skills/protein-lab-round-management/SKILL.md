---
name: protein-lab-round-management
description: "Use for creating, naming, organizing, and auditing Protein Lab local round directories under /Users/luke/Documents/Protein Lab, including plan files, FASTA/JSON inputs, result zips, reports, status logs, auth pending files, and traceability back to Feishu documents."
---

# Protein Lab Round Management

Use this skill for the local filesystem part of Protein Lab dry-lab work.

## Round Directory

Create rounds under `/Users/luke/Documents/Protein Lab`. Directory names should be stable, ASCII-friendly, and biologically meaningful:

```text
GRK4_C650_peptide_vs_ZDHHC17_ANK11-305/
EVTCGL_repeat_vs_ZDHHC17_ANK11-305/
GRK4_Cterm450-578_vs_ZDHHC17_full_and_ANK11-305/
```

## Standard Contents

Prefer this shape:

- `<slug>_plan.md`
- `<slug>.fasta`
- `<slug>_afserver.json` or another tool-specific input file
- downloaded raw result packages such as `folds_<slug>_afserver.zip`
- generated report directories
- `<slug>_interpretation_zh.md`
- `status_log.md`
- `auth_pending.json` when external authorization is pending

The local plan and `status_log.md` should link back to the Feishu experiment document when one exists.

## Initialization Script

Use the bundled script for a basic round skeleton:

```bash
python3 /Users/luke/plugins/protein-lab/skills/protein-lab-round-management/scripts/init_round.py --title "<任务标题>" --root "/Users/luke/Documents/Protein Lab"
```

The script is intentionally small. It creates the round directory, a plan file, and `status_log.md`; the science-specific content belongs in `protein-lab-experiment-design`.

## Status Log Rules

Record:

- Feishu task/document links
- exact input source and sequence versions
- tool names, parameters, seeds, job ids, and submission time
- download paths and file sizes
- blockers, pending authorization, queue status, and user hand-offs

If an online step fails, preserve the current local inputs and status before retrying.
