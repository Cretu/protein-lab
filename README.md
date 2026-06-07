# Protein Lab

Local Codex plugin for Protein Lab AlphaFold Server workflows.

This plugin captures project-specific guardrails for planning, interpreting, and reviewing Protein Lab dry-lab experiments, especially AF Server multi-job results, peptide or fragment comparisons, candidate refinement, and postmortems.

## Current Contents

- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `skills/protein-lab-afserver-workflows/SKILL.md`: Router and overview for Protein Lab work.
- `skills/protein-lab-experiment-design/SKILL.md`: AF Server experiment design and submission planning.
- `skills/protein-lab-afserver-interpretation/SKILL.md`: Raw AF Server result interpretation.
- `skills/protein-lab-candidate-refinement/SKILL.md`: Peptide, fragment, truncation, and mutation refinement.
- `skills/protein-lab-reporting-postmortem/SKILL.md`: Chinese report writing, Feishu-ready summaries, and postmortems.
- `skills/research-experiment-automation/SKILL.md`: End-to-end Feishu research task to local round to online tool workflow.
- `scripts/afserver_audit.py`: Lightweight AF Server zip or directory audit script.

## Notes

The plugin is intentionally local and project-specific for now. It should preserve Protein Lab lessons as reusable workflows without treating any single AF Server run as permanent biological proof.

## Core Principle

Use raw AF Server evidence first, then write bounded biological claims. The plugin should help Codex become more disciplined inside Protein Lab work, not more confident than the data.
