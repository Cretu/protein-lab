---
name: experiment
description: "Use for Protein Lab experiment thinking and design: defining biological questions, choosing constructs and controls, planning dry-lab panels, preparing reviewed inputs, setting decision criteria, designing next rounds, ranking candidates from evidence, and deciding stop/go before handing execution to tool-specific skills."
---

# Experiment

Use this skill for experiment design and next-round decision making. It owns the scientific plan, not platform operations.

## When To Use

- The user asks how to design, rerun, or revise a Protein Lab experiment.
- A task needs controls, comparison groups, construct boundaries, or candidate panels.
- Results already exist and the user asks what to test next.
- The user wants wet-lab shortlist logic or stop/go reasoning.

Do not use this skill for Feishu operations, local file housekeeping, final report writing, AlphaFold Server-specific submission and metric parsing, or Tamarind/PepMLM API mechanics.

## Required Planning Output

For a new or revised experiment, produce:

1. biological question and hypothesis
2. exact input sources, accessions, sequence lengths, and construct boundaries
3. comparison panel with job/candidate names and purpose
4. positive, negative, scrambled, truncation, mutation, or parent controls
5. tool-specific input requirements, but not tool operation details
6. interpretation rubric and conclusion boundary
7. decision that the result can change
8. next handoff: local folder, tool skill, reporting, or Feishu update

## Design Rules

- Define the biological question before choosing fragments or tools.
- Use reviewed canonical sequences for baselines or reruns; record accession and length.
- Keep historical noncanonical inputs as references unless the user explicitly asks to rerun them.
- Use domain-level or peptide-level designs when full-length membrane-protein context is likely to dominate the signal.
- Keep receptor construct, seed, chain order, and comparison conditions consistent unless intentionally varied.
- Put controls in the same batch when they answer the same claim.

## Common Experiment Patterns

- Full-length baseline: test whether any reliable global interface appears; weak full-length contacts should not become design anchors.
- Domain or fragment screen: compare overlapping constructs against the same receptor domain.
- Internal refinement: split a parent positive fragment into overlapping windows.
- Short peptide round: compare lead, mutations, scrambled negative, and benchmark control.
- Linker or repeat panel: compare monomer, direct repeat, linker repeat, and directional extension.

## Candidate Refinement

Rank or select candidates by:

1. same signal or receptor patch recurring across models or evidence sources
2. interface confidence from the relevant tool
3. relevant chain confidence and construct stability
4. direction versus parent, benchmark, mutation, truncation, or scrambled controls
5. simplicity: shorter, cleaner, and easier wet-lab constructs win when evidence is comparable

Prefer compact panels: primary lead, backup, benchmark or parent, negative/scrambled control, and one or two mechanistic mutants.

## Stop/Go

Go forward when the same signal survives multiple views, a smaller candidate matches or beats a longer benchmark, controls move sensibly, and more dry-lab variants would not change the next experiment.

Stop or deprioritize when gains come from one model only, flexible-tail artifacts, unexplained patch changes, unnecessary repeat additions, or terminal compensation that only optimizes a model artifact.

## Handoff

- Use `local-rounds` to create or update local files under the current or configured project workspace.
- Use `tool-af-server` when AlphaFold Server is the tool.
- Use `tool-tamarind-api` for shared Tamarind platform calls and `tool-tamarind-pepmlm` for PepMLM candidate work.
- Use `tool-modal` when the task needs custom Modal compute.
- Use `collab-feishu` only when the plan or result must be posted to Feishu.
- Use `reporting` for final summaries, reports, and postmortems.
- Use future `tool-*` skills for future dedicated tools.
