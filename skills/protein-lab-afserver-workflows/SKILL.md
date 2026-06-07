---
name: protein-lab-afserver-workflows
description: "Router skill for Protein Lab AlphaFold Server work in /Users/luke/Documents/Protein Lab. Use when the user asks broadly about Protein Lab experiments, AF Server workflows, GRK4, ZDHHC17, EVTCGL, peptide or fragment screens, candidate refinement, reporting, or turning lessons into plugin guardrails."
---

# Protein Lab AF Server Workflows

Use this as the router for Protein Lab dry-lab work. Prefer the narrower skills when the request is specific:

- `protein-lab-experiment-design`: design AF Server jobs, controls, manifests, and submission packages.
- `protein-lab-afserver-interpretation`: interpret raw AF Server zips or extracted job folders.
- `protein-lab-candidate-refinement`: rank, truncate, mutate, or stop peptide/fragment lead optimization.
- `protein-lab-reporting-postmortem`: write Chinese reports, Feishu-ready updates, and durable postmortems.
- `research-experiment-automation`: run the end-to-end Feishu task, experiment document, local round, online tool, result update, and task-comment loop.

## Project Defaults

- Work in `/Users/luke/Documents/Protein Lab` unless the user points elsewhere.
- Default language to Chinese in user-facing reports.
- Treat the plugin as local project memory, not a public biological knowledge base.
- Use raw AF Server JSON and job structure as source of truth; automatic reports are secondary.
- When blocked, leave a reusable guardrail, not just a one-off explanation.

## Shared Evidence Order

For peptide, fragment, truncation, mutation, or linker comparisons:

1. `ipTM` or chain-pair iPTM
2. peptide or fragment mean pLDDT
3. mean/min inter-chain PAE
4. token-level contact probability
5. cross-model convergence to the same receptor patch
6. directionality against controls, truncations, or mutations

## Shared Anti-patterns

- Do not assume longer peptides bind better.
- Do not assume direct repeats improve binding.
- Do not treat atom-distance proximity alone as interface evidence.
- Do not call a full-length membrane-protein AF failure a clean biological negative.
- Do not use one best model as enough when the other models diverge.
- Do not turn low-confidence flexible-tail contacts into design anchors.

## Useful Script

For raw AF Server result auditing, run:

```bash
python3 /Users/luke/plugins/protein-lab/scripts/afserver_audit.py <zip-or-dir> --out-dir <output-dir>
```

Use the script for extraction, metrics, and sanity checks. Use the skills for scientific judgment.
