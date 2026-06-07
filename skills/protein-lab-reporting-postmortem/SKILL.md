---
name: protein-lab-reporting-postmortem
description: "Use for writing Protein Lab Chinese experiment reports, Feishu-ready updates, conclusion sections, status logs, blocker summaries, postmortems, and durable skill/plugin guardrails after AF Server experiments or project workflow failures."
---

# Protein Lab Reporting And Postmortems

Use this skill when the user asks for a report, Feishu update, summary, conclusion, or lessons learned.

## Chinese Report Shape

Use this order unless the user asks otherwise:

1. 一句话结论
2. 任务与输入
3. 同口径指标表
4. 关键证据
5. 支持什么
6. 不能支持什么
7. 下一步建议
8. 风险边界

For Feishu-ready text, keep the conclusion compact, include only the essential table, and list attachments by filename if available.

Use `protein-lab-feishu-workflow` for the actual Feishu document updates, task comments, and completion calls. This skill owns the wording and postmortem content, not the Feishu API operation.

## Language Rules

- Use Chinese for user-facing reports by default.
- Keep claims conservative and actionable.
- Separate AF model interpretation from wet-lab interpretation.
- Do not let a report sound more certain than the raw metrics.

## Postmortem Shape

When the task had friction, write:

1. symptom
2. root cause
3. impact
4. what fixed it
5. durable guardrail for next time
6. whether a skill/plugin update is needed

## Common Guardrails To Capture

- Multi-job zips: split by job before comparing.
- Browser/AF Server submission: distinguish local input correctness from online submission timeout.
- CNB/plugin work: hidden `.codex-plugin` alone can make remote pages look empty; keep visible README and skill files.
- Long skill edits: use small, anchored patches and validate frontmatter.
- Scientific reruns: record sequence accession, length, seed, and why historical files are reference-only.

## Final Checks

Before saying a report is complete:

- ensure every number traces to raw JSON or a reviewed summary
- state the conclusion boundary
- include what not to do next
- add a reusable guardrail when the run exposed a workflow failure
