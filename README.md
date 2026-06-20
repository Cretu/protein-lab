# Protein Lab

Local Codex plugin for Protein Lab dry-lab problem solving and experiment workflows.

Protein Lab helps Codex triage life-science dry-lab tasks, plan experiments, manage local rounds, use external tools, work with collaboration platforms, interpret raw evidence, write Chinese summaries, and preserve project guardrails.

## Requirements

- Python 3.10+ (only the standard library is used by the bundled scripts; no `requirements.txt` needed).
- Network access for AlphaFold Server, Tamarind Bio API, Modal, and Feishu/Lark workflows that talk to those services.
- A platform-appropriate browser for AlphaFold Server submission flows. See `skills/tool-af-server/references/upload_recovery_os_notes.md` for OS-specific UI automation notes (macOS / Windows / Linux).

## Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `PROTEIN_LAB_ROOT` | Local project root for round folders and outputs. | `~/Documents/Protein Lab` |
| `PROTEIN_LAB_PLUGIN_ROOT` | Path to this checked-out plugin. Used in SKILL.md command snippets. | (unset; required) |
| `TAMARIND_API_KEY` | Tamarind Bio REST API key, used by `tool-tamarind-api`. | (unset) |
| `TAMARIND_BASE_URL` | Override Tamarind API base URL. | `https://app.tamarind.bio/api/` |

Set the first two once per environment, e.g.:

```bash
export PROTEIN_LAB_ROOT="$HOME/Documents/Protein Lab"
export PROTEIN_LAB_PLUGIN_ROOT="$HOME/plugins/protein-lab"
```

## Skill Map

The plugin name already provides the `protein-lab` namespace, so skill names stay short and action-oriented.

### Intake

- `skills/task-intake/SKILL.md`: Triage broad or ambiguous Protein Lab requests and route to the smallest useful skill.

### Experiment Work

- `skills/experiment/SKILL.md`: Design experiments, controls, candidate panels, next rounds, and stop/go decisions.
- `skills/local-rounds/SKILL.md`: Create and maintain local experiment round folders, file names, inputs, raw outputs, reports, and `status_log.md`.

### External Platforms And Tools

- `skills/tool-af-server/SKILL.md`: AlphaFold Server panel checks, JSON import, submission, queue tracking, downloads, raw result audit, and interpretation.
- `skills/tool-modal/SKILL.md`: Modal compute setup, cost guardrails, custom CPU/GPU pilot workflows, Volumes/Secrets handling, and Chai-1/ESMFold2/Boltz-2 style handoff.
- `skills/tool-tamarind-api/SKILL.md`: Tamarind Bio platform API preflight, tool discovery, submission, polling, downloads, and file operations.
- `skills/tool-tamarind-pepmlm/SKILL.md`: PepMLM payload preparation, result download handoff, raw result audit, candidate extraction, conservative interpretation, and AF/experiment shortlist handoff.
- `skills/collab-feishu/SKILL.md`: Feishu/Lark CLI, authorization, tasks, documents, comments, folders, and collaboration updates.

### Output

- `skills/reporting/SKILL.md`: Chinese reports, short updates, conclusion boundaries, postmortems, and durable guardrails.

## Scripts

All scripts are standard-library Python and read paths via `PROTEIN_LAB_ROOT` / arguments. None of them read API keys from disk.

- `skills/local-rounds/scripts/init_round.py`: Local round skeleton helper. Honors `PROTEIN_LAB_ROOT`.
- `skills/tool-af-server/scripts/afserver_audit.py`: AF Server zip/directory audit. Persists extraction under `<out-dir>/_extracted/` so JSON-recorded paths remain valid.
- `skills/tool-af-server/scripts/summarize_afserver_multijob_zip.py`: Deprecated shim; delegates to `afserver_audit.py`.
- `skills/tool-modal/references/modal-protein-lab-notes.md`: Modal docs summary and Protein Lab operating pattern for custom compute tasks.
- `skills/tool-tamarind-api/scripts/tamarind_api.py`: Tamarind REST API helper. Streaming uploads/downloads, exponential backoff on transient 429/5xx, `--confirm` required for `submit-job`/`submit-batch`.
- `skills/tool-tamarind-pepmlm/scripts/prepare_pepmlm_payload.py`: PepMLM submit-job payload builder. Rejects noncanonical residues unless `--allow-noncanonical`.
- `skills/tool-tamarind-pepmlm/scripts/inspect_pepmlm_result.py`: PepMLM raw result inventory, candidate extraction, and interpretation helper. Flags oversized text files in the inventory and only falls back to regex parsing for free-text formats.

## Testing

A minimal pytest suite covers the bundled scripts (payload validation, AF audit on a synthetic fixture, PepMLM inventory parsing):

```bash
python3 -m pytest tests/
```

## Principle

Use the smallest skill that matches the job. Keep local organization, collaboration platforms, scientific planning, tool-specific operation, and written outputs separate.
