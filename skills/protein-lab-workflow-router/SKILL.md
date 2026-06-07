---
name: protein-lab-workflow-router
description: "Router skill for Protein Lab dry-lab computational workflows in /Users/luke/Documents/Protein Lab. Use when the user asks broadly about Protein Lab experiments, life-science tools, Feishu research tasks, local rounds, tool execution, AlphaFold Server workflows, GRK4, ZDHHC17, EVTCGL, candidate refinement, reporting, or turning lessons into plugin guardrails."
---

# Protein Lab Workflow Router

Use this as the router for Protein Lab dry-lab computational work. Prefer the narrower skills when the request is specific:

- `protein-lab-feishu-workflow`: handle Feishu tasks, experiment docs, comments, folder links, and completion state.
- `protein-lab-round-management`: create and maintain local round directories, status logs, and traceability files.
- `protein-lab-experiment-design`: design dry-lab experiments, controls, manifests, FASTA, and tool input packages.
- `protein-lab-tool-execution`: operate online or local tools, submit jobs, track status, download raw outputs, and record failures.
- `protein-lab-afserver-interpretation`: interpret raw AF Server zips or extracted job folders.
- `protein-lab-candidate-refinement`: rank, truncate, mutate, or stop peptide/fragment lead optimization.
- `protein-lab-reporting-postmortem`: write Chinese reports, Feishu-ready updates, and durable postmortems.

## Current Tool Families

- AlphaFold Server is the first supported online tool family.
- Future tools should get their own execution or interpretation skill when the workflow develops enough repeated guardrails.

## Project Defaults

- Work in `/Users/luke/Documents/Protein Lab` unless the user points elsewhere.
- Default language to Chinese in user-facing reports.
- Treat the plugin as local project memory, not a public biological knowledge base.
- Use raw tool outputs, run configurations, job structure, and local status logs as source of truth; automatic reports are secondary.
- When blocked, leave a reusable guardrail, not just a one-off explanation.

## Shared Evidence Order

For peptide, fragment, truncation, mutation, or linker comparisons in structure-prediction workflows:

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

## Useful Scripts

For local round initialization, run:

```bash
python3 /Users/luke/plugins/protein-lab/skills/protein-lab-round-management/scripts/init_round.py --title "<任务标题>" --root "/Users/luke/Documents/Protein Lab"
```

For raw AF Server result auditing, run:

```bash
python3 /Users/luke/plugins/protein-lab/skills/protein-lab-afserver-interpretation/scripts/afserver_audit.py <zip-or-dir> --out-dir <output-dir>
```

Use scripts for deterministic scaffolding, extraction, metrics, and sanity checks. Use the skills for workflow routing and scientific judgment.
