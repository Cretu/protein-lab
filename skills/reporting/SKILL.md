---
name: reporting
description: "Use for Protein Lab writing outputs: Chinese reports, concise summaries, collaboration-ready update text, conclusion boundaries, blocker summaries, postmortems, lessons learned, and durable plugin or skill guardrails after dry-lab work."
---

# Reporting

Use this skill for written outputs. It produces content only; it does not post to Feishu, operate tools, or organize local folders.

## When To Use

- The user asks for a summary, report, conclusion, or next-step recommendation.
- A dry-lab result needs a conservative Chinese interpretation.
- A task had friction and needs a postmortem or reusable guardrail.
- The user wants a short update that can be shared elsewhere.

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

For short collaboration-ready updates, keep the conclusion compact, include only essential numbers, and list attachments by filename or path. Use `collab-feishu` for actual Feishu operations.

## Language Rules

- Use Chinese for user-facing reports by default.
- Keep claims conservative and actionable.
- Separate computational model interpretation from wet-lab interpretation.
- Do not make the report sound more certain than the raw evidence.
- Prefer "supports", "suggests", and "prioritizes" over "proves" for dry-lab outputs.

## Postmortem Shape

When the task had friction, write:

1. symptom
2. root cause
3. impact
4. what fixed it
5. durable guardrail
6. whether a skill/plugin update is needed

## Final Checks

- Every number should trace to raw data or reviewed summary.
- State the conclusion boundary.
- Include what not to do next.
- Capture repeatable workflow failures as guardrails.
