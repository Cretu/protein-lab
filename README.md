# Protein Lab

Local Codex plugin for Protein Lab dry-lab problem solving and experiment workflows.

Protein Lab helps Codex triage life-science dry-lab tasks, plan experiments, manage local rounds, use external tools, work with collaboration platforms, interpret raw evidence, write Chinese summaries, and preserve project guardrails.

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

- `skills/local-rounds/scripts/init_round.py`: Local round skeleton helper.
- `skills/tool-af-server/scripts/afserver_audit.py`: Lightweight AF Server zip or directory audit script.
- `skills/tool-af-server/scripts/summarize_afserver_multijob_zip.py`: Multi-job AF Server zip summary helper.
- `skills/tool-modal/references/modal-protein-lab-notes.md`: Modal docs summary and Protein Lab operating pattern for custom compute tasks.
- `skills/tool-tamarind-api/scripts/tamarind_api.py`: Tamarind REST API helper that reads `TAMARIND_API_KEY` from the environment.
- `skills/tool-tamarind-pepmlm/scripts/prepare_pepmlm_payload.py`: PepMLM submit-job payload builder.
- `skills/tool-tamarind-pepmlm/scripts/inspect_pepmlm_result.py`: PepMLM raw result inventory, candidate extraction, and interpretation helper.

## Principle

Use the smallest skill that matches the job. Keep local organization, collaboration platforms, scientific planning, tool-specific operation, and written outputs separate.
