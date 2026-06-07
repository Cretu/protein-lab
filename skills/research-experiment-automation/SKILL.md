---
name: research-experiment-automation
description: 用于把飞书科研任务自动执行成完整实验工作流。用户要求处理科研任务、从飞书任务创建实验文档、操作 AlphaFold Server 或其他在线科研工具、整理 Protein Lab 本地产物、解读实验结果并回写任务评论时必须使用。该 skill 适用于 /Users/luke/Documents/Protein Lab 工作台，优先用 lark-cli/API，必要时用 Browser 或 Computer Use 兜底；当用户提到科研任务、Protein Lab、实验文档、AlphaFold Server、结果解读、飞书任务评论或要把流程固化成 skill 时也应触发。
---

# Research Experiment Automation

## 目标

把一个指定飞书科研任务推进为可追踪的实验闭环：读取任务，理解与拆分实验，先创建并预填飞书实验文档，把文档链接回写到任务评论，再建立本地 round 目录，操作在线工具，解析结果，更新文档，并持续把简短状态和关键链接回写到任务评论。

默认中文输出。除非用户明确要求，不要自动扫描并处理整个任务列表；按用户指定的任务或当前任务清单里明确选中的任务执行。

默认端到端自行完成流程并交付成果，不按步骤停顿确认。只有在用户明确要求“按步骤确认”“一步一步推进”，或遇到登录/验证码/权限不足、付费/配额风险、会改变实验设计的重大冲突、需要用户选择科学判断边界、可能覆盖/删除已有飞书内容、结果与任务假设严重矛盾且会影响结论写法时，才停下来确认。用户回复“继续 / 执行 / 确认 / 完成了 / 好了”时，视为进入下一步。

## 固定上下文

- 飞书任务清单：`https://applink.feishu.cn/client/todo/task_list?guid=4aab1a22-13e0-452e-b2df-2be8cca53658`
- 实验文档目录：`https://stellarmonic.feishu.cn/drive/folder/XN43fKUBNlnOWSdILdLcW8Ownge?from=from_copylink`
- 本地工作台：`/Users/luke/Documents/Protein Lab`
- 结果判读：优先使用本插件的 `protein-lab-afserver-interpretation` skill；需要先做原始包审计时可运行 `/Users/luke/plugins/protein-lab/scripts/afserver_audit.py`
- 多 job 结果汇总：可用本 skill 的 `scripts/summarize_afserver_multijob_zip.py` 按 AlphaFold Server job 子目录解析 ranking/ipTM/pTM/PAE/contact。

## 访问策略

优先级：

1. `lark-cli --as user`：读取用户可见任务、云空间目录、创建/更新文档、任务评论。
2. `lark-cli --as bot`：仅在 bot 明确拥有目标资源权限时使用；bot 看不到用户个人资源是常见限制。
3. Browser / Computer Use：用于 AlphaFold Server、需要登录或没有 API 覆盖的在线工具。

任务评论限制：评论读取与回写只能使用 `lark-cli`。不要用飞书 UI 查看、确认、添加或编辑评论；如果当前 `lark-cli` 暴露的 API 无法读取历史评论，应明确记录“CLI 暂无可用评论读取能力”，并继续用 `lark-cli task +comment` 做后续状态回写。

运行前先做只读 preflight：

```bash
lark-cli task tasklists get --as user --params '{"tasklist_guid":"4aab1a22-13e0-452e-b2df-2be8cca53658"}'
lark-cli task tasklists tasks --as user --params '{"tasklist_guid":"4aab1a22-13e0-452e-b2df-2be8cca53658","completed":false,"page_size":20}'
lark-cli drive files list --as user --params '{"folder_token":"XN43fKUBNlnOWSdILdLcW8Ownge","order_by":"EditedTime","direction":"DESC","page_size":10}'
```

如果出现 `need_user_authorization`，按缺失 scope 最小授权，例如：

```bash
lark-cli auth login --scope "task:tasklist:read space:document:retrieve"
```

如果 bot 报 `App scope not enabled` 或 `Invoker is unauthorized`，向用户报告缺失 scope 或目标资源授权，不要绕过权限。

### 飞书权限预检与授权等待

科研任务的末端通常需要三类 user scope：读取任务/目录、更新文档/附件、评论并完成任务。不要等所有实验产物都完成后才第一次检查“完成任务”权限；在开始执行前或创建文档后，先用最小风险命令确认当前 token 是否具备后续必需 scope。若最终需要调用 `lark-cli task +complete`，提前确认是否已有 `task:task:write`，否则把它列为待授权项。

如果缺 scope，优先使用 `--no-wait --json` 生成一次设备授权链接，并把返回的 `device_code`、`verification_url`、`expires_in`、本地生成时间写入 round 目录的 `status_log.md` 或 `auth_pending.json`。把 `verification_url` 原样给用户；不要 URL 编码/解码，不要改写成 Markdown 链接，不要在同一轮展示 URL 后马上阻塞执行 `--device-code`。

等待授权时遵循这个规则：

- 用户明确说“完成了/好了/已授权”后，再运行 `lark-cli auth login --device-code <device_code>` 完成 token 换取。
- heartbeat 或自动轮询中，如果没有用户确认，不要用短 timeout 反复启动 `--device-code`，也不要在旧设备码未过期时反复生成新链接；这会作废上一轮链接，用户越点越失败。
- 只有旧设备码已过期，或者用户反馈链接不可用时，才生成新的 `--no-wait --json` 链接，并更新 `auth_pending.json`。
- 授权未完成时，不要把任务标记完成，不要删除 heartbeat/automation；只报告“产物已完成，待授权关闭任务”。

## 工作流

### 1. 获取任务

输入可以是任务清单、任务链接、任务 GUID、或用户口头指定的列表项。任务 applink 中 `/client/todo/task?guid=...` 的 `guid` 是 task GUID；`/client/todo/task_list?guid=...` 的 `guid` 是 tasklist GUID。

读取任务时至少收集：

- 标题、描述、截止时间、负责人、已有评论、附件或链接
- 用户明确要求完成的任务项
- 是否需要在线工具、湿实验建议、文档产物或结果判读

若 API 读不到评论，应报告 CLI 能力缺口，不要切换到飞书 UI。发评论、创建文档、上传文件、提交外部工具任务属于本 workflow 的正常动作，默认直接执行并在 `status_log.md` 与任务评论里留下可追踪记录；只有动作会造成不可逆删除、权限外授权、费用/配额异常消耗或与用户明确偏好冲突时才确认。低风险只读浏览不需要额外确认。

### 2. 理解与拆分

把任务转成实验计划，明确：

- 科学问题和可检验假设
- 输入序列、蛋白、突变、对照、工具、参数
- 预期输出：FASTA、AF Server JSON、结果 zip、报告、中文解读、飞书文档链接
- 需要人工介入的点：登录、验证码、付费/排队、上传敏感文件、结果解释不确定、湿实验优先级选择

遇到不确定但影响实验设计的内容，优先在任务评论区或对用户提问；不影响当前准备工作的内容先继续推进。

### 3. 创建实验文档并回写任务评论

理解完任务后，优先创建飞书实验文档，而不是先建本地目录。原因是飞书文档是协作入口和任务的外部可见产物，应尽早把已经明确的背景、目标、输入、实验设计和待办写进去，并把文档链接同步回任务评论。

先读取实验文档目录中最近编辑的 2-3 篇文档，参考其目录与写法。若 CLI 无权限，先报告需要 `space:document:retrieve`，不要用飞书 UI 兜底创建或评论。

标题格式：

```text
YYYY-MM-DD 任务标题
```

正文默认结构：

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

如果最近文档有更明确结构，以最近文档为准。当前 Protein Lab 最近实验文档采用 H1 `背景 / 目标 / 数据 / 实验`，不要写成通用日志式 H2 结构。创建时先填写已经确定的部分，例如背景文档、任务目标、序列来源、基础数据、执行策略、具体实验标题、方案及参数、当前未完成的结论占位。不要等结果回来才创建空文档。

创建命令示例：

```bash
cd "/Users/luke/Documents/Protein Lab/<round_dir>"
lark-cli docs +create --as user --folder-token XN43fKUBNlnOWSdILdLcW8Ownge --title "YYYYMMDD-<任务标题>" --markdown @feishu_doc_initial.md
```

`docs +create --markdown @file` 只能引用当前工作目录内的相对路径，不要传绝对路径。若 `auth check` 提示旧 scope `space:document:create` 缺失，但 `auth status` 已有 `docx:document:create`，可先用 `docs +create --dry-run` 确认当前 CLI 实际调用能力，再执行创建。

当前 `docs +update` 对既有文档中的 `<task>`、`<view>`、`<file>` 等飞书内部块支持有限，覆盖文档时这些标签可能被移除。需要附件块时，用 `lark-cli docs +media-insert --type file` 上传本地 plan、FASTA、JSON、报告等真实文件附件。最近实验文档里的在线预览附件对应 `file.view_type=2`；用 `docs +media-insert --file-view preview` 生成。默认 `card` 会生成 `view_type=1`，不符合当前实验文档样式。

插入输入文件时，位置应在 `### 方案及参数` 部分内，通常放在参数与输入校验之后、`### 结论及建议` 之前。默认只上传方案 plan 和 AlphaFold Server JSON；FASTA 保留在本地 round，不上传到飞书文档，除非用户明确要求。可用：

```bash
lark-cli docs +media-insert --as user --doc "<doc_url>" --file "<file>" --type file --file-view preview --selection-with-ellipsis "JSON 包含 3 个 job，seed 均为"
```

若多次对同一 selection 插入附件，后插入的文件会更靠近 selection；为保持 plan、FASTA、JSON 顺序，可按 JSON、FASTA、plan 的反序执行插入。

创建成功后，`docs +create` 可能返回 `https://www.feishu.cn/docx/...` 这类通用域名。不要直接把该链接写入任务评论；应重新读取目标文件夹条目，使用 `drive files list` 返回的租户域名 canonical URL，例如 `https://stellarmonic.feishu.cn/docx/...`。如果已经评论了错误链接，可用 generic API 删除本人任务评论：

```bash
lark-cli api DELETE /open-apis/task/v2/comments/<comment_id> --as user --params '{"user_id_type":"open_id","resource_id":"<task_guid>","resource_type":"task"}'
```

创建成功后，立即用 `lark-cli task +comment --as user` 回写任务评论：

```text
已建立实验文档： <doc_url> 当前状态：已完成任务理解与实验设计，准备建立本地 round 并生成 AlphaFold 输入。下一步：生成 FASTA/AF Server JSON 并提交预测。
```

任务评论里的文档 URL 后面必须用普通空格分隔，不要在 `--content` 中写 `\n` 转义序列紧跟 URL；部分飞书任务评论会把字面量 `\n` 解析进链接尾部。若需要多行评论，应使用真实换行并先 dry-run/确认渲染；默认用单行简短状态更新。

### 4. 建立本地 round

飞书文档创建并回写任务评论后，在 `/Users/luke/Documents/Protein Lab` 下创建主题目录。目录名用英文/数字/短横线/下划线，保留生物学对象与实验目标，例如：

```text
GRK4_C650_peptide_vs_ZDHHC17_ANK11-305/
EVTCGL_repeat_vs_ZDHHC17_ANK11-305/
GRK4_Cterm450-578_vs_ZDHHC17_full_and_ANK11-305/
```

目录内优先保留：

- `<slug>_plan.md`
- `<slug>.fasta`
- `<slug>_afserver.json` 或其他在线工具输入文件
- 下载的原始结果包，例如 `folds_<slug>_afserver.zip`
- `<zip_stem>-report/`
- `<slug>_interpretation_zh.md`
- `status_log.md`，记录关键动作、时间、链接和阻塞点

本地 plan 和 `status_log.md` 要记录飞书实验文档链接，保持本地 round 与飞书文档互相可追踪。

可用 bundled script 初始化目录：

```bash
python3 /Users/luke/plugins/protein-lab/skills/research-experiment-automation/scripts/init_round.py --title "<任务标题>" --root "/Users/luke/Documents/Protein Lab"
```

### 5. 操作在线工具

AlphaFold Server 是当前已知可用工具。其他在线工具不限，但必须按同一记录标准处理：输入、参数、提交时间、job id / URL、下载结果、失败原因。

AlphaFold 类任务：

1. 在本地生成 FASTA 和 AF Server JSON。
2. 用 Browser / Computer Use 打开 `https://alphafoldserver.com/`。
3. 如果遇到登录、验证码、权限弹窗、付费、长时间排队，向用户汇报并等待。
4. JSON 上传后的 `Submit N jobs as drafts` 只是把任务保存为 draft，不是正式提交。必须在历史列表里逐条打开 draft，进入 `Continue and preview job`，核对 job name、seed、链长和 Remaining jobs 后点击 `Confirm and submit job`。提交成功的直接证据是 Remaining jobs 按提交数量下降，且历史列表里对应任务出现 `In progress`/进度状态与新的 Modified 时间。
5. 提交后记录每个 job 的名称、提交时间、seed、链长、Remaining jobs 变化和当前状态；同步更新本地 `status_log.md`、飞书实验文档的 `### 方案及参数` 或提交记录位置，并用任务评论做简短状态回写。
6. 下载 zip 后放入当前 round 目录。
7. 运行 AlphaFold 解读脚本生成标准报告。

结果下载时，优先使用 AlphaFold Server 的多选批量下载，保存到当前 round 目录，文件名用 `folds_<slug>_afserver.zip`。保存面板可能记住上一次目录；保存前用路径跳转或文件存在性检查确认目标目录，避免把结果落到旧 round。下载后用 `ls -lh` 或等价方式确认文件大小和时间。

效率优化边界：

- 官方支持的自动化入口是 AlphaFold Server JSON：一次 JSON 可包含多个 job，用于重复建模或小规模互作筛选。优先在本地程序化生成 JSON，减少手工录入和多次文件上传。
- 截至当前资料，AlphaFold Server 没有公开、稳定、文档化的“直接提交/批量 confirm job”API；导入 JSON 后仍需要从 draft 进入正式提交确认。不要把未公开的浏览器内部接口写成默认路径，除非用户明确要求探索并接受可能失效、可能违反服务策略、需要处理登录凭据的风险。
- 可接受的提效方式是用浏览器自动化替代坐标点击：通过 Playwright/CDP 或 Computer Use 的稳定元素定位完成 `Upload JSON`、打开每个 draft、`Continue and preview job`、`Confirm and submit job`，并在每次正式提交前核对 job name、seed、链长和配额变化。
- 如果任务规模明显增大，优先评估本地 AlphaFold 3 / Boltz / Chai 等可脚本化替代方案，而不是把 AlphaFold Server 当作高通量提交后端。

### 6. 结果处理与判读

AlphaFold 结果必须按已有标准解释，不只报最高分：

- pTM：整体折叠可信度，不等于界面可信度
- ipTM：界面可信度；柔性肽体系要保守
- pLDDT：链/局部可信度
- inter-chain PAE：局部相对定位可信度
- 模型一致性：5 个模型是否收敛到同一 patch
- 对照差异：WT、突变、hard negative/scrambled 是否能区分

多 job AlphaFold Server zip 需要额外小心：不同 job 内部都会有 `model_0`、`model_1` 等同名模型，通用自动报告脚本可能把模型名、任务名、序列展示或图像输出混在一起。做 N/M/C、WT/mutant、多个候选肽这类比较时，必须按 zip 解包后的每个 job 子目录分别读取 `job_request.json`、`summary_confidences_*.json`、`full_data_*.json`，先确认 job name 与链 A 序列，再汇总每个 job 的 best model、ipTM、pTM、inter-chain PAE、contact probability 和跨模型热点一致性。不要只看合并报告的第一张排序表。

可用内置脚本先生成逐 job 摘要：

```bash
python3 /Users/luke/plugins/protein-lab/skills/research-experiment-automation/scripts/summarize_afserver_multijob_zip.py "<result.zip>" --out "<slug>_afserver_multijob_summary.md"
python3 /Users/luke/plugins/protein-lab/skills/research-experiment-automation/scripts/summarize_afserver_multijob_zip.py "<result.zip>" --format json --out "<slug>_afserver_multijob_summary.json"
```

输出结论必须区分：

- 支持什么
- 不能支持什么
- 哪些只是候选热点或假设生成
- 下一步实验或设计优先级

### 7. 更新飞书文档与任务

将本地计划、输入、结果报告、中文 interpretation、关键图片/附件链接整理进实验文档。文档更新后，用 `lark-cli task +comment --as user` 在任务评论区做简短状态更新，包含有价值链接和阻塞点。

结果附件默认放在 `### 结论及建议` 的结果正文之后。上传中文解读、PDF/HTML 报告和原始结果 zip；FASTA 默认不上传。仍使用 `docs +media-insert --file-view preview` 生成在线预览块。更新文档后必须 fetch 一次确认正文、表格和 `<view type="2">` 附件块仍在正确章节，避免 `docs +update` 覆盖掉已有附件块。

`docs +update` 的参数和 Markdown 渲染要按实际 CLI 验证，不要沿用未经验证的旧写法。已知注意点：

- 当前可用路径通常是 `lark-cli docs +update --as user --doc "<doc_url>" --mode replace_range --selection-with-ellipsis "<原文片段>" --markdown @file`；若加 `--api-version v2` 报 `--command is required`，回退到已验证的 v1/默认命令。
- 更新前让 selection 包含足够稳定的前后文；更新后用 `docs +fetch` 检查旧占位文本是否消失、关键结论是否出现、附件块是否还在。
- 飞书 Markdown 表格不一定支持 GitHub 风格右对齐标记。若 fetch 后出现 `{align="right"}` 之类字面量，改成普通表格并再次 replace。
- 多个附件插入到同一 selection 时，最终顺序可能与上传顺序相反；插入后用 fetch 验证文件名列表和位置，不要只相信命令退出码。

评论格式建议：

```text
已建立实验文档：<doc_url>
当前状态：已完成输入设计 / 已提交 AlphaFold / 结果已下载并解读 / 等待登录或权限
关键结论：<一句话>
下一步：<需要用户确认或后续动作>
```

不要在评论里堆完整报告；完整内容放实验文档和本地 round。

若用户要求“完成任务”或 heartbeat 指令包含“完成任务”，文档和评论完成后还必须调用：

```bash
lark-cli task +complete --as user --task-id "<task_guid>"
```

只有该命令成功返回后，才算飞书任务闭环完成。若报缺少 `task:task:write`，按“飞书权限预检与授权等待”处理，并在评论/heartbeat 中说明“结果已交付，待授权关闭任务”。

## 当前已知权限缺口

在本机模拟中，user 身份读取任务清单缺 `task:tasklist:read`，读取云空间目录缺 `space:document:retrieve`；bot 对目标科研任务清单没有访问权，且云空间读取缺 `space:document:retrieve` scope。执行真实任务前优先补 user 授权。

## 完成检查

交付前确认：

1. 任务是否有实验文档链接。
2. 本地 round 是否包含计划、输入、原始结果、报告和中文解读。
3. 飞书文档是否包含任务来源、方法、结果、结论和下一步。
4. 任务评论是否有简短状态、文档链接、关键结论或阻塞点。
5. 对外提交、评论、上传、权限变更都符合用户授权。
6. 如果任务要求完成飞书待办，`lark-cli task +complete` 是否已成功；未成功时不得删除对应 automation，也不得说任务已完成。
