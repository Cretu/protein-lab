---
name: tool-af-server
description: "Use for all Protein Lab AlphaFold Server work: reviewing AF Server panels, checking JSON/FASTA/manifests, browser import, draft verification, formal submission, queue tracking, downloads, raw zip/folder auditing, multi-job result separation, summary_confidences/full_data JSON interpretation, PAE/contact/iPTM evidence checks, and AF-specific candidate evidence."
---

# Tool AF Server

Use this skill for the whole AlphaFold Server tool surface. It owns AF Server-specific mechanics and interpretation rules.

Keep general experiment design in `experiment`, local folder hygiene in `local-rounds`, final writing in `reporting`, and Feishu operations in `collab-feishu`.

## When To Use

- Preparing or reviewing AF Server JSON, FASTA, manifests, seeds, chain order, or job panels.
- Importing JSON, creating drafts, verifying previews, submitting jobs, tracking queue state, and downloading result zips.
- Auditing raw AF Server zips or extracted folders.
- Interpreting AF Server metrics, PAE, contact probability, iPTM, pLDDT, and multi-job batches.
- Comparing peptide, fragment, truncation, repeat, linker, mutation, GRK4, ZDHHC17, or EVTCGL AF Server results.

## Before Submission

- Confirm the biological question, comparison panel, and controls with `experiment`.
- Keep FASTA, AF Server JSON, manifest, raw downloads, and `status_log.md` together through `local-rounds`.
- Verify accession, sequence length, construct boundaries, seed, chain count, chain order, and job names.
- Keep historical noncanonical inputs as references only unless the user explicitly asks to rerun them.

## Browser Submission

1. Upload the JSON.
2. Treat `Submit N jobs as drafts` as draft creation only.
3. Open each draft and continue to preview.
4. Verify job name, seed, chain count, chain lengths, and intended chain order.
5. Formally submit only after preview verification.
6. Record remaining jobs, job URLs or IDs, and queue state in `status_log.md`.
7. Download raw zip results into the active local round.

Stop for login, captcha, quota exhaustion, payment, or irreversible submission uncertainty. A browser timeout is not evidence that local inputs are wrong.

## Raw Result Audit

Inventory the result package before judging it. If it is a zip, determine whether it contains one job or many jobs. For each job, pair `summary_confidences_*.json` with matching `full_data_*.json`.

Run the bundled audit script:

```bash
python3 /Users/luke/plugins/protein-lab/skills/tool-af-server/scripts/afserver_audit.py <zip-or-dir> --out-dir <output-dir>
```

For legacy multi-job zip summaries:

```bash
python3 /Users/luke/plugins/protein-lab/skills/tool-af-server/scripts/summarize_afserver_multijob_zip.py <zip-path> --out <output-file>
```

Use generated reports, PAE SVGs, and PDFs only as secondary views.

## Interpretation Order

- Start with 5-model consistency, not only the best model.
- Inspect `ranking_score`, `iptm`, `ptm`, chain-pair iPTM, chain-pair PAE min, mean inter-chain PAE, max/mean contact probability, and chain mean pLDDT.
- For peptide jobs, isolate peptide pLDDT from receptor pLDDT.
- Require low PAE and high contact to recur around the same receptor region before claiming a candidate patch.
- Distinguish token-level contact probability from atom-distance proximity.
- Never compare `model_0` across jobs without job labels.

## Confidence Language

- Strong AF interface signal: high iPTM, relevant chain confidence, low inter-chain PAE, high contact probability, and same-patch recurrence.
- Medium signal: useful for ranking and follow-up design, not atom-level mechanism.
- Weak/negative structural signal: low iPTM and high inter-chain PAE; reject this model as a design basis, not the biology itself.
- Artifact risk: flexible tail contacts, direct repeats, full-length membrane-protein noise, or a single isolated best model.

## Protein Lab Guardrails

- Full-length GRK4 vs full-length ZDHHC17 can fail at chain placement while single-chain pLDDT remains moderate.
- ZDHHC17 ANK-focused jobs are often more interpretable than full-length membrane-protein jobs for short peptide questions.
- `EVTCGL` being strong does not mean `EVTCGL` direct repeat is stronger.
- A parent fragment with two possible contacts needs truncation evidence before assigning the real blocking plane.
- A delayed job is usually queue or service state unless raw evidence says the sequence is unsupported.

## Handoff

- Send next-round design or wet-lab shortlist decisions to `experiment`.
- Send Chinese summaries or postmortems to `reporting`.
- Use `collab-feishu` only when the result needs to be posted to Feishu/Lark.
