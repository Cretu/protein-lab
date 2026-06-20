---
name: collab-feishu
description: "Use for all Protein Lab Feishu/Lark collaboration work: lark-cli installation checks, login and authorization, task list reading, task comments, task completion, document creation or updates, folder operations, permission preflight, and linking Feishu resources to local rounds."
---

# Collab Feishu

Use this skill for Feishu/Lark only. It is the collaboration platform skill, not the experiment planner, report writer, or scientific tool runner.

## When To Use

- The user mentions Feishu, Lark, task list, document, docx, comment, folder, permission, authorization, or `lark-cli`.
- A local Protein Lab result needs to be posted to a task or document.
- A Feishu task/document is the source of a Protein Lab experiment.
- Feishu access is blocked by missing scopes, bot/user permission, or login state.

## Fixed Protein Lab Context

- Task list: `https://applink.feishu.cn/client/todo/task_list?guid=4aab1a22-13e0-452e-b2df-2be8cca53658`
- Experiment docs folder: `https://stellarmonic.feishu.cn/drive/folder/XN43fKUBNlnOWSdILdLcW8Ownge?from=from_copylink`
- Local root: `${PROTEIN_LAB_ROOT}` (default `~/Documents/Protein Lab`)

## CLI Preflight

Before mutating Feishu resources, check `lark-cli` and access with read-only calls when possible:

```bash
lark-cli task tasklists get --as user --params '{"tasklist_guid":"4aab1a22-13e0-452e-b2df-2be8cca53658"}'
lark-cli task tasklists tasks --as user --params '{"tasklist_guid":"4aab1a22-13e0-452e-b2df-2be8cca53658","completed":false,"page_size":20}'
lark-cli drive files list --as user --params '{"folder_token":"XN43fKUBNlnOWSdILdLcW8Ownge","order_by":"EditedTime","direction":"DESC","page_size":10}'
```

Prefer `--as user` for user-visible tasks, docs, comments, and folder operations. Use `--as bot` only when bot access to the target resource is confirmed.

## Authorization Guardrails

- Request the minimum missing scope.
- Prefer `--no-wait --json` for device authorization links.
- Store pending auth details in `auth_pending.json` or in the active `status_log.md`.
- Do not generate repeated device codes while an unexpired code is pending.
- Do not mark tasks complete while authorization is unresolved.

## Documents And Comments

Use `reporting` to produce wording. Use `collab-feishu` to create, update, comment, and complete.

Compact task comment shape:

```text
当前状态：<已规划 / 已提交 / 结果已下载 / 已解读 / 等待授权>
关键结论：<一句话>
产物位置：<local path or doc URL>
下一步：<next action>
```

After creating or updating a document, read it or list the folder again to verify the canonical tenant URL, such as `https://stellarmonic.feishu.cn/docx/...`.
