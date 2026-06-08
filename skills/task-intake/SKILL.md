---
name: task-intake
description: "Use as the Protein Lab intake and triage skill when the request is broad, ambiguous, or spans multiple abilities. Route dry-lab questions to experiment, local-rounds, tool-af-server, collab-feishu, or reporting; decide whether to answer a temporary problem directly or start a structured experiment workflow."
---

# Task Intake

Use this skill like a front desk for Protein Lab work. It should make the task actionable and choose the smallest next skill, not perform every step itself.

## When To Use

- The user asks a broad Protein Lab question and the next skill is unclear.
- The task may involve several areas such as experiment planning, local files, AlphaFold Server, Feishu, and reporting.
- The user brings a temporary dry-lab problem that may not deserve a full workflow.
- A workflow is blocked and needs rerouting.

## Route By User Intent

- "这是什么问题 / 该怎么推进 / 帮我判断下一步" -> clarify the intent here, then route.
- "规划实验 / 设计对照 / 做下一轮 / 候选怎么改" -> `experiment`.
- "建本地目录 / 初始化 round / status_log / 整理输入和结果" -> `local-rounds`.
- "AlphaFold Server / AF Server / JSON 导入 / 提交 / 下载 / 解读 zip" -> `tool-af-server`.
- "飞书 / Lark / 任务 / 文档 / 评论 / 授权 / CLI" -> `collab-feishu`.
- "总结 / 报告 / 复盘 / 结论边界 / 可分享短文案" -> `reporting`.

## Intake Checklist

Before routing, identify:

- task type: temporary question, experiment planning, tool operation, result interpretation, collaboration update, or report
- source of truth: local files, raw tool output, Feishu document, user-provided text, or public reference
- urgency: answer now, create a local round, submit a tool job, or wait for results
- missing blocker: input file, authorization, login, raw result zip, or user decision

## Routing Rules

- Do not assume every request starts from Feishu.
- Do not create a local round for a one-off question unless the work will produce files or continue later.
- If a dedicated tool skill exists, use it instead of generic browser or CLI habits.
- If the task exposes a repeatable failure, route final lessons to `reporting` for a durable guardrail.

## Default Context

- Local project root: `/Users/luke/Documents/Protein Lab`
- User-facing language: Chinese unless the user requests otherwise.
- Evidence priority: raw outputs and local source files first, generated summaries second.
