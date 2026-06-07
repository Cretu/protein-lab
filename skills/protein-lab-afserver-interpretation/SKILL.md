---
name: protein-lab-afserver-interpretation
description: "Use for interpreting Protein Lab AlphaFold Server zips, extracted result folders, multi-job batches, raw summary_confidences/full_data JSON, PAE/contact metrics, and side-by-side comparisons for GRK4, ZDHHC17, EVTCGL, short peptide, fragment, truncation, repeat, linker, or mutation experiments."
---

# Protein Lab AF Server Interpretation

Use this skill when results have returned from AF Server.

## First Pass

1. Inventory the result package before judging it.
2. If it is a zip, inspect whether it contains one job or many jobs.
3. For each job, pair `summary_confidences_*.json` with matching `full_data_*.json`.
4. Read metrics per job and per model; do not compare `model_0` across jobs without job labels.
5. Use generated reports, PAE SVGs, and PDFs only as secondary views.

Run the bundled audit script when raw files are present:

```bash
python3 /Users/luke/plugins/protein-lab/skills/protein-lab-afserver-interpretation/scripts/afserver_audit.py <zip-or-dir> --out-dir <output-dir>
```

For legacy multi-job zip summaries, use the co-located helper:

```bash
python3 /Users/luke/plugins/protein-lab/skills/protein-lab-afserver-interpretation/scripts/summarize_afserver_multijob_zip.py <zip-path> --out-dir <output-dir>
```

## Interpretation Order

- Start with 5-model consistency, not only the best model.
- For each model, inspect `ranking_score`, `iptm`, `ptm`, chain-pair iPTM, chain-pair PAE min, mean inter-chain PAE, max/mean contact probability, and chain mean pLDDT.
- For peptide jobs, isolate peptide pLDDT from receptor pLDDT.
- For candidate patch claims, require low PAE and high contact to recur around the same receptor region across models.
- Distinguish token-level contact probability from atom-distance contact.

## Confidence Language

- Strong AF interface signal: high iPTM, good peptide/fragment pLDDT for the relevant chain, low inter-chain PAE, high contact probability, and same-patch recurrence.
- Medium signal: usable for ranking and follow-up design, not for atom-level mechanism.
- Weak/negative structural signal: low iPTM and high inter-chain PAE; can reject this model as a design basis, but not the biology itself.
- Artifact risk: flexible tail contacts, direct repeats, full-length membrane-protein noise, or a single isolated best model.

## Protein Lab Examples To Generalize

- Full-length GRK4 vs full-length ZDHHC17: low iPTM and high inter-chain PAE mean no usable complex pose, even when single-chain pLDDT is moderate.
- EVTCGL direct repeat: monomer can be strong while unlinked repeat becomes a flexible tail; longer is not automatically stronger.
- GRK4 540-560 refinement: overlapping truncations can show which parent-fragment patch survives as a competitive blocking plane.
- Short peptide final rounds: stop when the shortest lead preserves the same patch and does not improve with extra terminal compensation.

## Report Boundary

Always write both:

- what the AF Server result supports
- what it does not prove

Never write AF evidence as if it were wet-lab validation.

## Handoff

- Send ranked or next-round candidate decisions to `protein-lab-candidate-refinement`.
- Send Chinese final summaries, Feishu-ready updates, or postmortems to `protein-lab-reporting-postmortem`.
