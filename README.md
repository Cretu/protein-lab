# Protein Lab

Local Codex plugin for Protein Lab multi-tool dry-lab workflows.

This plugin captures project-specific guardrails for planning, running, interpreting, and reviewing Protein Lab computational biology experiments. AlphaFold Server is the first supported tool family, but the platform is intended to grow across life-science dry-lab tools for structure prediction, sequence analysis, omics, target biology, candidate design, and evidence synthesis.

## Current Contents

- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `skills/protein-lab-workflow-router/SKILL.md`: Router and overview for Protein Lab work.
- `skills/protein-lab-feishu-workflow/SKILL.md`: Feishu task, document, comment, and completion workflow.
- `skills/protein-lab-round-management/SKILL.md`: Local round directory creation, status logs, and traceability.
- `skills/protein-lab-experiment-design/SKILL.md`: Dry-lab experiment design, controls, and tool input planning.
- `skills/protein-lab-tool-execution/SKILL.md`: Online or local tool execution, job tracking, downloads, and retries.
- `skills/protein-lab-afserver-interpretation/SKILL.md`: Raw AlphaFold Server result interpretation.
- `skills/protein-lab-candidate-refinement/SKILL.md`: Peptide, fragment, truncation, and mutation refinement.
- `skills/protein-lab-reporting-postmortem/SKILL.md`: Chinese report writing, Feishu-ready summaries, and postmortems.
- `skills/protein-lab-afserver-interpretation/scripts/afserver_audit.py`: Lightweight AF Server zip or directory audit script.
- `skills/protein-lab-afserver-interpretation/scripts/summarize_afserver_multijob_zip.py`: Multi-job AF Server zip summary helper.
- `skills/protein-lab-round-management/scripts/init_round.py`: Local round skeleton helper.

## Notes

The plugin is intentionally local and project-specific for now. It should preserve Protein Lab lessons as reusable workflows without treating any single AF Server run as permanent biological proof.

## Core Principle

Use raw tool outputs and source evidence first, then write bounded biological claims. The plugin should help Codex become more disciplined inside Protein Lab work, not more confident than the data.
