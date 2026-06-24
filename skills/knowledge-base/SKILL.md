---
name: knowledge-base
description: "Use for connecting, initializing, indexing, reading, and safely updating a Protein Lab team wiki or knowledge base such as local Markdown/Git wiki, Feishu Wiki, Obsidian, or a team docs directory while keeping facts separate from executable skills."
---

# Knowledge Base

Use this skill for team/project knowledge. The wiki stores facts, evidence, literature notes, decisions, experiment records, and durable lessons. Skills store executable procedures.

## When To Use

- The user asks to search, initialize, index, or update a Protein Lab wiki.
- A task needs project background, previous decisions, literature notes, or experiment history.
- A lesson should be preserved but is not itself an executable workflow.
- The team needs a local Markdown/Git wiki, Feishu Wiki, Obsidian vault, or docs folder connected to Protein Lab.

## Default Local Wiki Structure

- `projects/`: project background and goals
- `experiments/`: experiment records and round indexes
- `tools/`: tool usage lessons
- `protocols/`: wet-lab and dry-lab procedures
- `decisions/`: key decisions and ADR-like notes
- `literature/`: paper and database notes
- `guardrails/`: failure lessons and stop rules

## Local Markdown Helper

Initialize or index a local wiki:

```bash
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/knowledge-base/scripts/knowledge_base.py" init --root <wiki-root>
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/knowledge-base/scripts/knowledge_base.py" index --root <wiki-root>
```

The helper writes only local Markdown structures and JSON indexes. For Feishu Wiki or Obsidian, use the matching external Codex skills after `setup` records the intended root or URL.

## Read Rules

- Prefer the configured wiki root from setup.
- When inside a configured project, prefer that project's `.protein-lab/project.json` wiki root over the global registry.
- Treat a shared team wiki as explicit configuration, not an accidental fallback.
- Cite the wiki file path or document URL when using it as evidence.
- Distinguish old project context from current raw tool evidence.
- If wiki content conflicts with raw outputs, inspect raw outputs first and note the conflict.

## Write Rules

- Ask whether the note is meant to become durable team knowledge before writing.
- Do not store secrets, personal credentials, private tokens, or raw account exports.
- Put experiment outputs in `local-rounds`; put summarized durable lessons or indexes in wiki.
- Keep skill changes separate from wiki updates.

## Handoff

- Use `skill-curator` to decide whether a lesson should update a skill instead.
- Use `reporting` to draft readable summaries before writing team-facing wiki notes.
- Use `collab-feishu` or Obsidian skills when the wiki backend is not local Markdown.
