---
name: protein-lab-feishu-workflow
description: "Use for Protein Lab Feishu/Lark research task workflows: reading task lists or task GUIDs, creating experiment documents, handling user/bot permission preflight, writing task comments, inserting document attachments, updating docs, and completing tasks after dry-lab work is delivered."
---

# Protein Lab Feishu Workflow

Use this skill for the Feishu-facing part of Protein Lab work. It should not design the science, run tools, or interpret results by itself; hand those parts to the relevant Protein Lab skills.

## Fixed Context

- Task list: `https://applink.feishu.cn/client/todo/task_list?guid=4aab1a22-13e0-452e-b2df-2be8cca53658`
- Experiment docs folder: `https://stellarmonic.feishu.cn/drive/folder/XN43fKUBNlnOWSdILdLcW8Ownge?from=from_copylink`
- Local workspace: `/Users/luke/Documents/Protein Lab`

## Access Policy

Prefer `lark-cli --as user` for user-visible tasks, docs, comments, and folder operations. Use `--as bot` only when bot access to the target resource is confirmed.

Do not use Feishu UI for task comments. Comments must be read or written through `lark-cli`; if comment reading is unavailable, record that limitation and continue with `lark-cli task +comment` for new status updates.

Run a read-only preflight before mutating Feishu resources:

```bash
lark-cli task tasklists get --as user --params '{"tasklist_guid":"4aab1a22-13e0-452e-b2df-2be8cca53658"}'
lark-cli task tasklists tasks --as user --params '{"tasklist_guid":"4aab1a22-13e0-452e-b2df-2be8cca53658","completed":false,"page_size":20}'
lark-cli drive files list --as user --params '{"folder_token":"XN43fKUBNlnOWSdILdLcW8Ownge","order_by":"EditedTime","direction":"DESC","page_size":10}'
```

## Authorization Guardrails

- If scopes are missing, request the minimum user authorization needed.
- Prefer `--no-wait --json` for device authorization links, then wait for the user to say authorization is complete before exchanging the code.
- Store pending device auth details in the round directory as `auth_pending.json` or in `status_log.md`.
- Do not repeatedly generate device codes while a previous unexpired code is pending.
- Do not mark tasks complete while authorization is unresolved.

## Document Workflow

Create the Feishu experiment document before building the local round when the task starts from Feishu. The document is the external collaboration surface.

Default document shape:

```md
# 背景
# 目标
# 数据
## 基础数据
## 执行策略
# 实验
## <实验标题>
### 方案及参数
### 结论及建议
```

Use recent documents in the experiment folder as style references when available. After `docs +create`, re-read the folder and use the tenant canonical URL such as `https://stellarmonic.feishu.cn/docx/...`, not a generic `https://www.feishu.cn/docx/...` URL.

## Comments And Completion

Use compact task comments:

```text
已建立实验文档：<doc_url>
当前状态：<已完成输入设计 / 已提交工具 / 结果已下载并解读 / 等待权限>
关键结论：<一句话>
下一步：<后续动作或待确认事项>
```

Only say a Feishu task is complete after `lark-cli task +complete --as user --task-id "<task_guid>"` succeeds. If `task:task:write` is missing, state that the result is delivered but task closure is pending authorization.

## Hand-offs

- Use `protein-lab-experiment-design` for scientific plan and inputs.
- Use `protein-lab-round-management` for local round files.
- Use `protein-lab-tool-execution` for online tool operation.
- Use `protein-lab-reporting-postmortem` for final Chinese report and task-ready summary.
