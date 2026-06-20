---
name: tool-tamarind-pepmlm
description: "Use for Protein Lab Tamarind PepMLM work: preparing pepmlm payloads, submitting or polling PepMLM jobs through tool-tamarind-api, downloading raw results, auditing result zip/folders, extracting peptide candidates, ranking shortlists conservatively, and handing candidates to AF Server or experiment design."
---

# Tool Tamarind PepMLM

Use this skill for the full PepMLM workflow. PepMLM is a Tamarind Bio tool that generates peptide binder candidates from a target protein sequence. It is a generator, not binding validation.

Keep Tamarind platform calls in `tool-tamarind-api`, local folders in `local-rounds`, AF validation in `tool-af-server`, experiment panel decisions in `experiment`, and final prose in `reporting`.

## When To Use

- The user mentions Tamarind PepMLM, `pepmlm`, peptide binder generation, target sequence to peptide candidates, or PepMLM results.
- A Protein Lab task needs PepMLM candidates for a target protein or construct.
- A downloaded PepMLM zip/folder needs auditing, candidate extraction, shortlist generation, or conservative interpretation.

## API Settings

Submit with Tamarind `type` set to `pepmlm`.

Required settings:

- `targetSequence`: target protein sequence to design peptides against
- `peptideLength`: peptide length; Tamarind default is `15`
- `numDesigns`: string enum `"1"`, `"2"`, `"4"`, `"8"`, `"16"`, `"32"`; Tamarind default is `"8"`

Use the app API docs as the operational source of truth:

- `https://app.tamarind.bio/api-docs/pepmlm`
- `https://app.tamarind.bio/openapi.yaml`

## Prepare Payload

Create payloads with the bundled script:

```bash
python3 /Users/luke/plugins/protein-lab/skills/tool-tamarind-pepmlm/scripts/prepare_pepmlm_payload.py \
  --input <target.fasta-or-sequence.txt> \
  --job-name <jobName> \
  --peptide-length 15 \
  --num-designs 8 \
  --out <jobName>_pepmlm_payload.json
```

The script accepts FASTA or plain sequence, normalizes whitespace, validates `jobName`, and writes a Tamarind `/submit-job` payload.

## Run Through Tamarind API

Use `tool-tamarind-api` for real API calls:

```bash
python3 /Users/luke/plugins/protein-lab/skills/tool-tamarind-api/scripts/tamarind_api.py submit-job --payload <payload.json>
python3 /Users/luke/plugins/protein-lab/skills/tool-tamarind-api/scripts/tamarind_api.py jobs --job-name <jobName>
python3 /Users/luke/plugins/protein-lab/skills/tool-tamarind-api/scripts/tamarind_api.py download-result --job-name <jobName> --out <raw-zip>
```

Record payload path, job name, settings, submission response, polling state, raw zip path, and any blocker in `status_log.md`.

## Inspect Results

Always audit raw outputs before interpretation:

```bash
python3 /Users/luke/plugins/protein-lab/skills/tool-tamarind-pepmlm/scripts/inspect_pepmlm_result.py \
  <raw-zip-or-folder> \
  --out-dir <inspection-dir> \
  --expected-length 15 \
  --top-n 12
```

Outputs:

- `pepmlm_result_inventory.tsv`: raw file inventory
- `pepmlm_candidates.tsv`: standardized candidate table
- `pepmlm_inspection_summary.json`: machine-readable summary
- `pepmlm_interpretation.md`: conservative Chinese interpretation draft

If the result package has an unknown structure, the script still writes an inventory and states that no candidate table was identified.

## Interpretation Rules

- Start from raw result inventory, then candidate table. No raw evidence means no conclusion.
- Treat PepMLM ranking as generator priority only; it is not binding strength, degradation ability, or mechanism proof.
- Prefer candidates that are sequence-valid, expected length, non-duplicate, well-ranked or well-scored in the raw output, and easy to validate in AF Server or wet lab.
- Preserve diversity when shortlisting; do not pick only near-identical top rows.
- Flag but do not automatically discard issue motifs such as long homopolymers, noncanonical residues, N-glycosylation motifs, high cysteine burden, or adjacent cysteines.
- Do not claim target patch, binding mode, or interface confidence from PepMLM alone.

## Protein Lab Handoff

After inspection, produce:

1. candidate table path
2. recommended shortlist and backup candidates
3. rejected or deprioritized candidates with reasons
4. AF Server validation panel suggestion
5. wet-lab or experiment-design handoff
6. conclusion boundary

Use `tool-af-server` to validate shortlisted peptide-target complexes. Use `experiment` when the user asks which candidates should enter wet-lab panels.

## Protein Lab Guardrails

- In GRK4/ZDHHC17 peptide work, PepMLM should start from the current target construct and validated anchor context, not a blank generic binder-discovery framing.
- A PepMLM candidate that scores well still needs AF Server or wet-lab validation before being described as stronger.
- If the result parser cannot identify candidate sequences, stop at audit and ask for raw output review rather than inventing a shortlist.
