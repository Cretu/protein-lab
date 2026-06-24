---
name: skill-curator
description: "Use for managing Protein Lab research skills: discovering, evaluating, importing, splitting, merging, upgrading, and deciding whether a new lesson belongs in plugin core skills, team research skills, external Codex skills, or the knowledge-base wiki."
---

# Skill Curator

Use this skill to keep Protein Lab skills clean, reusable, and separate from team-specific knowledge. It decides where a new capability or lesson belongs.

## When To Use

- The user wants to add, review, rename, split, or merge research skills.
- A repeated workflow or failure lesson should become durable.
- The team wants to reuse an external Codex skill or local team skill.
- A new fact might belong in wiki, not in a skill.

## Skill Classes

- Plugin core skills: bundled with Protein Lab, cross-team, stable, and generic.
- Team research skills: team/project-specific procedures that can live in a team repo or local skills folder.
- External Codex skills: existing skills such as life-science databases, literature search, Feishu/Lark, Obsidian, or browser automation.

## Placement Rules

- Put stable repeatable procedures in skills.
- Put project facts, literature notes, experiment results, and team decisions in `knowledge-base`.
- Put third-party tool operation in `tool-*` skills created through `tool-creator`.
- Put collaboration platform actions in `collab-*` skills.
- Do not put large project history directly in a `SKILL.md`; link to a wiki or reference file when needed.

## Classification Helper

For a quick deterministic first pass:

```bash
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/skill-curator/scripts/classify_research_asset.py" \
  --text "<lesson or capability>"
```

Use the helper as a first pass only. Final placement should consider reuse, privacy, and whether the content is a procedure or a fact.

## Review Checklist

- Is the content reusable outside one experiment?
- Does it require deterministic scripts?
- Is it project/team-specific?
- Does it contain raw scientific facts or conclusions that should be cited?
- Would loading it in every skill waste context?
- Does an existing Codex skill already cover most of it?

## Handoff

- Use `tool-creator` for new third-party tool skills.
- Use `knowledge-base` for durable facts, experiment records, literature notes, and decisions.
- Use `setup` if team skill roots or wiki roots are not configured.
