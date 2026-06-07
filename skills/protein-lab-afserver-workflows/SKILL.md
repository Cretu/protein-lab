---
name: protein-lab-afserver-workflows
description: Use for Protein Lab AlphaFold Server experiment planning, raw result interpretation, multi-job zip review, peptide or fragment comparison, candidate refinement, and postmortems in /Users/luke/Documents/Protein Lab. Especially relevant for GRK4, ZDHHC17, EVTCGL, short peptide, truncation, mutation, and side-by-side AF Server tasks.
---

# Protein Lab AF Server Workflows

Use this skill when working in `/Users/luke/Documents/Protein Lab` on AlphaFold Server dry-lab experiments.

## Default Workflow

1. Start from the source of truth:
   - experiment plan or manifest when designing jobs
   - AF Server JSON request when checking what was submitted
   - raw `summary_confidences_*.json` and `full_data_*.json` when interpreting results
   - downloaded zip structure when handling multi-job results
2. Classify the task before judging:
   - single job interpretation
   - multi-job batch summary
   - side-by-side peptide, fragment, truncation, or mutation comparison
   - candidate refinement or lead selection
   - postmortem and skill hardening
3. Prefer conservative conclusions:
   - say what the AF result supports
   - say what it does not prove
   - separate structural hypotheses from wet-lab evidence
4. If the run had blockers, convert them into durable guardrails before finishing.

## Evidence Order

For peptide or fragment binding comparisons, rank evidence in this order:

1. `ipTM` / chain-pair iPTM
2. peptide or fragment mean pLDDT
3. mean and minimum inter-chain PAE
4. token-level contact probability
5. whether multiple models converge on the same receptor patch
6. whether controls, truncations, or mutations move in the expected direction

Do not use atom-distance proximity alone as high-confidence interface evidence. Flexible peptides can lie near a surface without a reliable interface.

## Multi-job Guardrails

- Never use a mixed automatic report as the primary source for side-by-side conclusions.
- Split multi-job zips by job directory or job name before comparing.
- For each job, read its own `summary_confidences_*.json` and `full_data_*.json`.
- Treat repeated filenames such as `model_0` as job-local, not globally comparable.
- When a job is pending or delayed while peers finish, record it as a queue/state issue unless raw evidence shows the sequence is unsupported.

## Protein Lab Anti-patterns

Avoid these shortcuts:

- assuming longer peptides bind better
- assuming direct repeats improve binding
- assuming a Cys-adjacent window is mechanistically meaningful without controls
- treating full-length membrane-protein AF noise as a clean negative biological result
- treating a single best model as enough when the other models diverge
- using low-confidence contacts from flexible tails as design anchors

## Reporting Shape

For Chinese reports, prefer:

1. one-sentence conclusion
2. same-metric comparison table
3. key evidence and patch recurrence
4. conclusion boundary
5. next wet-lab or next AF experiment recommendation
6. postmortem guardrails if the task encountered friction
