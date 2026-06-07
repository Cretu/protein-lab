---
name: protein-lab-candidate-refinement
description: "Use for Protein Lab peptide, fragment, truncation, mutation, linker, repeat, and lead optimization decisions. Covers candidate ranking, stop/go calls, shortest-lead selection, motif residue hierarchy, receptor patch recurrence, and wet-lab shortlist recommendations for AF Server-derived hypotheses."
---

# Protein Lab Candidate Refinement

Use this skill when moving from raw AF results to next candidates.

## Ranking Function

Rank candidates by:

1. same-patch recurrence across models
2. iPTM and chain-pair iPTM
3. peptide/fragment pLDDT
4. low inter-chain PAE at the proposed interface
5. high token-level contact probability at the proposed interface
6. direction versus controls or parent constructs
7. simplicity: shorter, cleaner, and easier wet-lab constructs win when evidence is comparable

## Refinement Patterns

- Parent-to-window: split a promising parent fragment into overlapping windows; the surviving window defines the next hypothesis.
- Window-to-hotspot: mutate or truncate around recurring contact residues; test whether the patch remains.
- Lead-to-shortest: shorten only while preserving the same receptor patch and evidence quality.
- Lead-to-control: keep positive, scrambled, and key-anchor mutants close to the lead panel.
- Repeat/linker: compare direct repeat, linker repeat, and directional extension; do not treat repeats as automatic interface expansion.

## Stop/Go Rules

Go to wet-lab shortlist when:

- the same patch recurs across the model ensemble
- a smaller candidate matches or beats a longer benchmark
- controls move in a biologically sensible direction
- further AF changes would not change the next experiment

Stop or deprioritize when:

- gains come only from one model
- the new contact is a flexible tail artifact
- the candidate changes patch without a good reason
- added aromatics, repeats, or terminal residues make the model less stable

## Protein Lab Lessons

- `EVTCGL` being strong does not mean `EVTCGL` direct repeat is stronger.
- A short lead can beat its longer ancestor if it keeps the patch and improves pLDDT.
- A residue can be strengthening without being absolutely required.
- Removing a terminal residue can improve convergence; adding terminal compensation can hurt.
- A parent fragment with two possible contacts needs truncation evidence before assigning the real blocking plane.

## Wet-lab Recommendation Shape

Give a small shortlist:

1. primary lead
2. strongest backup
3. original benchmark or parent control
4. negative/scrambled control
5. one or two mechanistic mutants

Prefer a compact panel that answers a decision over a broad exploratory list.
