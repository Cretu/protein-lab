---
name: protein-lab-experiment-design
description: "Use for designing Protein Lab dry-lab experiments and tool input packages: selecting chains, fragments, controls, mutants, repeats, linkers, seeds, manifests, FASTA/JSON submissions, interpretation rubrics, and conclusion boundaries for AlphaFold Server and future computational biology tools."
---

# Protein Lab Experiment Design

Use this skill before submitting or rerunning dry-lab jobs for Protein Lab. AlphaFold Server is the first supported tool family, but design decisions should stay tool-aware rather than AF-only.

## Required Output

For a new experiment, create or update:

1. plan markdown with background, hypothesis, exact inputs, jobs, controls, interpretation rubric, and conclusion boundary
2. FASTA when useful for human review
3. tool-specific input such as an AF Server JSON request
4. manifest CSV with job id, chain or sample mapping, purpose, and expected comparison
5. `status_log.md` with timestamps and submission/download state

## Design Rules

- Define the biological question before choosing fragments.
- Use reviewed canonical sequences when the task is a baseline or rerun; record accession and length.
- Keep historical noncanonical inputs as references only, never silently mix them into a canonical rerun.
- Use domain-level or peptide-level jobs when full-length membrane-protein context is likely to dominate the signal.
- Use the same receptor construct, seed, and chain order across comparison panels unless the difference is intentional.
- Put positive, negative, scrambled, truncation, or mutation controls in the same batch when they answer the same claim.

## Common Panels

- Full-length baseline: use to test whether AF finds any reliable global interface; do not use weak full-length contacts for design.
- Domain/fragment screen: compare overlapping fragments against the same receptor domain to localize candidate patches.
- Internal refinement: split a parent positive fragment into overlapping windows to test whether the parent signal survives.
- Short peptide round: compare lead, one-position mutations, scrambled negative, and known positive controls.
- Linker/repeat panel: compare monomer, direct repeat, linker repeat, and directional extension; do not assume length is beneficial.

## Handoff

- Use `protein-lab-round-management` to create the local directory and status log before or during design.
- Use `protein-lab-tool-execution` after inputs are reviewed and ready to submit.
- Use `protein-lab-feishu-workflow` when the design came from a Feishu task or needs a Feishu experiment document.

## Built-in Protein Lab Lessons

- GRK4/ZDHHC17 full-length baseline can fail at chain placement while single-chain pLDDT remains moderate; this points away from interface design, not away from biology.
- ZDHHC17 ANK-focused jobs are often more interpretable than full-length ZDHHC17 membrane-protein jobs for short peptide questions.
- GRK4 C-terminal windows need overlapping controls; a parent fragment with two low-PAE regions does not prove both are independent binding planes.
- A delayed AF Server job in a batch is usually a queue/state problem unless raw evidence shows the sequence is unsupported.

## Stop Conditions

Stop expanding AF designs when:

- the same patch and lead survive multiple small panels
- new changes only test aesthetic variants without a decision they can change
- a result is strong enough to justify wet-lab ranking
- further AF would likely optimize against model artifacts rather than biology
