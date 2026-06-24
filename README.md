# Protein Lab

Local Codex plugin for portable Protein Lab dry-lab workspaces, onboarding, tool workflows, knowledge management, and experiment execution.

Protein Lab helps Codex onboard new devices and teams, diagnose local environments, configure project workspaces, manage local rounds, use external tools, curate research skills, connect team knowledge bases, work with collaboration platforms, interpret raw evidence, write Chinese summaries, and preserve project guardrails.

## Requirements

- Python 3.10+ (only the standard library is used by the bundled scripts; no `requirements.txt` needed).
- Network access for AlphaFold Server, Tamarind Bio API, Modal, and Feishu/Lark workflows that talk to those services.
- A platform-appropriate browser for AlphaFold Server submission flows. See `skills/tool-af-server/references/upload_recovery_os_notes.md` for OS-specific UI automation notes (macOS / Windows / Linux).

## Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `PROTEIN_LAB_ROOT` | Optional fallback local project root for round folders and outputs. `setup` config and current project/cwd usually take precedence. | `~/Documents/Protein Lab` |
| `PROTEIN_LAB_PLUGIN_ROOT` | Path to this checked-out plugin. Used in SKILL.md command snippets. | (unset; required) |
| `TAMARIND_API_KEY` | Tamarind Bio REST API key, used by `tool-tamarind-api`. | (unset) |
| `TAMARIND_BASE_URL` | Override Tamarind API base URL. | `https://app.tamarind.bio/api/` |

Set `PROTEIN_LAB_PLUGIN_ROOT` for command snippets. Set `PROTEIN_LAB_ROOT` only when you want an environment fallback instead of project-local setup:

```bash
export PROTEIN_LAB_PLUGIN_ROOT="$HOME/plugins/protein-lab"
# optional fallback only
export PROTEIN_LAB_ROOT="$HOME/Documents/Protein Lab"
```

Local plugin/team configuration is written by `setup` to:

```bash
~/.config/protein-lab/config.json
```

This file is a global local registry. Each configured project also gets an isolated project config:

```bash
<workspace-root>/.protein-lab/project.json
```

Project-local config stores that project's workspace root, team/project label, optional Feishu URLs, wiki root, and enabled capabilities. This lets multiple local Protein Lab projects run in parallel without sharing rounds, wiki context, or collaboration links by accident. Neither global nor project-local config may contain API keys, tokens, cookies, or passwords.

## Skill Map

The plugin name already provides the `protein-lab` namespace, so skill names stay short and action-oriented.

### Intake

- `skills/setup/SKILL.md`: First-run onboarding, environment doctor, local workspace selection, configuration, and smoke-test guidance.
- `skills/task-intake/SKILL.md`: Triage broad or ambiguous Protein Lab requests and route to the smallest useful skill.

### Experiment Work

- `skills/experiment/SKILL.md`: Design experiments, controls, candidate panels, next rounds, and stop/go decisions.
- `skills/local-rounds/SKILL.md`: Create and maintain local project workspaces and experiment round folders, file names, inputs, raw outputs, parsed outputs, reports, and `status_log.md`.

### Knowledge And Skills

- `skills/knowledge-base/SKILL.md`: Connect, initialize, index, read, and safely update a local/team wiki or knowledge base.
- `skills/skill-curator/SKILL.md`: Decide whether research lessons belong in plugin core skills, team research skills, external Codex skills, or wiki.

### External Platforms And Tools

- `skills/tool-creator/SKILL.md`: Scaffold and harden new `tool-*` integrations for API, CLI, web, and compute tools.
- `skills/tool-af-server/SKILL.md`: AlphaFold Server panel checks, JSON import, submission, queue tracking, downloads, raw result audit, and interpretation.
- `skills/tool-modal/SKILL.md`: Modal compute setup, cost guardrails, custom CPU/GPU pilot workflows, Volumes/Secrets handling, and Chai-1/ESMFold2/Boltz-2 style handoff.
- `skills/tool-tamarind-api/SKILL.md`: Tamarind Bio platform API preflight, tool discovery, submission, polling, downloads, and file operations.
- `skills/tool-tamarind-pepmlm/SKILL.md`: PepMLM payload preparation, result download handoff, raw result audit, candidate extraction, conservative interpretation, and AF/experiment shortlist handoff.
- `skills/collab-feishu/SKILL.md`: Feishu/Lark CLI, authorization, tasks, documents, comments, folders, and collaboration updates.

### Output

- `skills/reporting/SKILL.md`: Chinese reports, short updates, conclusion boundaries, postmortems, and durable guardrails.

## Scripts

All scripts are standard-library Python and read paths via arguments, current project/cwd, local config, or environment fallbacks. None of them read API keys from disk.

- `skills/setup/scripts/protein_lab_setup.py`: First-run configuration and read-only doctor reports. Writes local config only in `configure` mode and never stores secrets.
- `skills/local-rounds/scripts/init_round.py`: Local round skeleton helper. Resolves the workspace from explicit `--root`, nearest `.protein-lab/project.json`, current directory, global config, env, then fallback.
- `skills/knowledge-base/scripts/knowledge_base.py`: Local Markdown wiki initialization, indexing, and safe note writing.
- `skills/tool-creator/scripts/scaffold_tool_skill.py`: Minimal `tool-*` skill scaffold generator.
- `skills/skill-curator/scripts/classify_research_asset.py`: First-pass classifier for deciding whether a lesson belongs in a tool skill, core skill, team skill, or wiki.
- `skills/tool-af-server/scripts/afserver_audit.py`: AF Server zip/directory audit. Persists extraction under `<out-dir>/_extracted/` so JSON-recorded paths remain valid.
- `skills/tool-af-server/scripts/summarize_afserver_multijob_zip.py`: Deprecated shim; delegates to `afserver_audit.py`.
- `skills/tool-modal/references/modal-protein-lab-notes.md`: Modal docs summary and Protein Lab operating pattern for custom compute tasks.
- `skills/tool-tamarind-api/scripts/tamarind_api.py`: Tamarind REST API helper. Streaming uploads/downloads, exponential backoff on transient 429/5xx, `--confirm` required for `submit-job`/`submit-batch`.
- `skills/tool-tamarind-pepmlm/scripts/prepare_pepmlm_payload.py`: PepMLM submit-job payload builder. Rejects noncanonical residues unless `--allow-noncanonical`.
- `skills/tool-tamarind-pepmlm/scripts/inspect_pepmlm_result.py`: PepMLM raw result inventory, candidate extraction, and interpretation helper. Flags oversized text files in the inventory and only falls back to regex parsing for free-text formats.

## Testing

A minimal pytest suite covers the bundled scripts (payload validation, AF audit on a synthetic fixture, PepMLM inventory parsing):

```bash
python3 -m pip install -e ".[test]"
python3 -m pytest tests/
```

Release checks:

```bash
python3 /Users/luke/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /path/to/protein-lab
python3 /Users/luke/.codex/skills/.system/skill-creator/scripts/quick_validate.py /path/to/protein-lab/skills/<skill>
python3 -m compileall skills tests
```

## Principle

Use the smallest skill that matches the job. Keep setup, local organization, wiki knowledge, skill curation, collaboration platforms, scientific planning, tool-specific operation, and written outputs separate.
