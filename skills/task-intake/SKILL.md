---
name: task-intake
description: "Use as the Protein Lab intake and triage skill when the request is broad, ambiguous, or spans multiple abilities. Route setup/configuration, local workspaces, tool creation, skill curation, knowledge-base/wiki work, dry-lab experiments, tool execution, Feishu collaboration, or reporting to the smallest useful skill."
---

# Task Intake

Use this skill like a front desk for Protein Lab work. It should make the task actionable and choose the smallest next skill, not perform every step itself.

## When To Use

- The user asks a broad Protein Lab question and the next skill is unclear.
- The task may involve several areas such as setup, project workspace files, wiki, experiment planning, AlphaFold Server, Modal compute, Tamarind/PepMLM, Feishu, and reporting.
- The user brings a temporary dry-lab problem that may not deserve a full workflow.
- A workflow is blocked and needs rerouting.

## Route By User Intent

- "这是什么问题 / 该怎么推进 / 帮我判断下一步" -> clarify the intent here, then route.
- "新设备 / 刚安装 / 初始化 / 配置 / 环境检查 / doctor / workspace / 工作目录" -> `setup`.
- "wiki / 知识库 / 文献笔记 / 项目背景 / 历史实验 / guardrails / 团队知识" -> `knowledge-base`.
- "新增工具 / 接入平台 / API 工具 / CLI 工具 / 网页工具 / record & play / 自动化一个工具" -> `tool-creator`.
- "科研 skill / 管理 skills / 拆分 skill / 经验该进 skill 还是 wiki / 引入外部 skill" -> `skill-curator`.
- "规划实验 / 设计对照 / 做下一轮 / 候选怎么改" -> `experiment`.
- "建本地目录 / 初始化 round / status_log / 整理输入和结果" -> `local-rounds`.
- "AlphaFold Server / AF Server / JSON 导入 / 提交 / 下载 / 解读 zip" -> `tool-af-server`.
- "Modal / modal.com / 云端 GPU / serverless GPU / Chai-1 / ESMFold2 / Boltz-2 / 自定义算力 pilot" -> `tool-modal`.
- "Tamarind API / API key / /tools / /submit-job / /jobs / 下载结果" -> `tool-tamarind-api`.
- "PepMLM / pepmlm / peptide binder / 候选肽生成 / PepMLM 结果解读" -> `tool-tamarind-pepmlm`.
- "飞书 / Lark / 任务 / 文档 / 评论 / 授权 / CLI" -> `collab-feishu`.
- "总结 / 报告 / 复盘 / 结论边界 / 可分享短文案" -> `reporting`.

## Intake Checklist

Before routing, identify:

- environment state: configured workspace, new device, or blocked setup
- task type: temporary question, experiment planning, tool operation, result interpretation, collaboration update, or report
- source of truth: local files, raw tool output, wiki, Feishu document, user-provided text, or public reference
- urgency: answer now, create a local round, submit a tool job, inspect downloaded results, or wait for results
- missing blocker: workspace config, wiki root, input file, authorization, login, raw result zip, or user decision

## Routing Rules

- Do not assume every request starts from Feishu.
- Do not create a local round for a one-off question unless the work will produce files or continue later.
- Do not assume `${PROTEIN_LAB_ROOT}` is the workspace on a new device; use `setup` or current project/cwd.
- When multiple local projects may exist, prefer the nearest `.protein-lab/project.json` and do not reuse another project's wiki, Feishu links, or active round.
- If a dedicated tool skill exists, use it instead of generic browser or CLI habits.
- If a new dedicated tool is needed, route to `tool-creator` before hand-writing an ad hoc procedure.
- If a lesson is project fact or history, route to `knowledge-base`; if it is repeatable procedure, route to `skill-curator`.
- If the task exposes a repeatable failure, route final lessons to `reporting` for a durable guardrail.

## Default Context

- Local project root: current project/cwd or the configured `workspace_root` from `~/.config/protein-lab/config.json`.
- Plugin scripts root: `${PROTEIN_LAB_PLUGIN_ROOT}` — wherever this plugin is installed.
- User-facing language: Chinese unless the user requests otherwise.
- Evidence priority: raw outputs and local source files first, generated summaries second.
