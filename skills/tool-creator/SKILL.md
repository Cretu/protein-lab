---
name: tool-creator
description: "Use for extending Protein Lab with a new third-party bioinformatics or dry-lab tool by designing and scaffolding a dedicated tool-* skill for API, CLI, web, or compute platforms, including preflight, inputs, run flow, raw output audit, interpretation boundaries, handoff, and tests."
---

# Tool Creator

Use this skill when a new third-party platform, API, CLI, web tool, or cloud compute workflow should become a reusable Protein Lab `tool-*` capability.

## When To Use

- The user says a new tool/platform should be added to Protein Lab.
- A task repeats manual API, CLI, browser, or cloud-compute steps that should become a skill.
- A web workflow can benefit from Codex browser control, record/play, or a reproducible submission checklist.
- A tool needs a conservative result-audit and interpretation boundary before it can feed experiments.

## Tool Types

- API: read docs/OpenAPI first, then create helper scripts and dry-run/preflight behavior.
- CLI: check install/auth/version, define dry-run, capture outputs, and parse artifacts.
- Web: use browser skills or record/play capabilities when available; preserve a manual fallback.
- Compute: define budget, GPU/CPU, persistence, retries, and output download rules.

## Scaffold

Create a minimal `tool-*` skill with:

```bash
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/tool-creator/scripts/scaffold_tool_skill.py" \
  --skills-root "${PROTEIN_LAB_PLUGIN_ROOT}/skills" \
  --tool-name tool-example \
  --tool-kind api \
  --display-name "Example Tool"
```

The scaffold is only a starting point. Fill in facts from primary docs, real UI/API behavior, and a smoke test before considering the tool usable.

## Required Tool Skill Contract

Every `tool-*` skill must define:

- trigger phrases and when not to use it
- preflight checks for install/auth/network/account state
- exact input requirements and where to store them
- submit/run/poll/download behavior
- raw output inventory before interpretation
- conservative interpretation boundary
- handoff to `local-rounds`, `experiment`, `knowledge-base`, or `reporting`
- validation and no-secret checks

Never let a tool skill claim scientific validation just because a job ran successfully.

## Handoff

- Use `setup` if the local environment is not ready.
- Use `knowledge-base` to record durable tool lessons and team usage notes.
- Use `skill-curator` when deciding whether a lesson belongs in an existing skill, a new tool skill, or the wiki.
