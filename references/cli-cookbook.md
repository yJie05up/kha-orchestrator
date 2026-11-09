# kha CLI 官方示例校验清单（以本机 `kha docs` 为最终依据）

> 适用于 KHA 文档 2026-11-09 访问所示版本。用户的本地 CLI 可能更新。此处只列官方网页明确出现的用法；未列操作必须先用 `kha docs` 确认。

## 前置准备

```bash
kha version
kha whoami
kha docs
kha install-skill -g
```

- 安装官方 `kha` Skill 后，它通常在 `~/.agents/skills/kha/`（用户级）或 `./.agents/skills/kha/`（项目级）。本 Skill 是决策叠加层，**不要替换** 官方 Skill。
- `kha login` 由用户自己在本地终端无回显输入 Key；不得在 宿主对话中粘贴 Key。CI 可参考 `kha login --api-key-stdin`，安全地从受保护标准输入注入。
- `kha docs <resource> <command>` 查看匹配本机版本的具体参数与示例。

## 资源管理（已见官方实例）

```bash
kha environments list --limit 20
kha environments get "$ENVIRONMENT_ID"
kha agents create --file worker.json
kha agents create --file coordinator.json
kha sessions create --agent "$AGENT_ID" --environment "$ENVIRONMENT_ID" --title "可核验任务"
kha sessions create --file session.json
```

- `worker.json` 和 `coordinator.json` 需填真实字段和 ID；只有 `Agent ID + Environment ID` 是创建 Session 的必填项。
- `--file` 支持 JSON / YAML；不要与 `--agent`, `--environment`, `--title` 等字段选项混用。
- 创建 Agent/Environment 后保存返回 ID；执行环境新建/更新后等待 `build_status == ready`。旧版 ready 可能被平台选中，不能误当新配置生效。

## 执行、观察、取回

```bash
kha sessions send "$SESSION_ID" "请按要求完成并给出证据与产物。"
kha sessions get "$SESSION_ID"
kha sessions events "$SESSION_ID" --limit 20
kha sessions attach "$SESSION_ID" --since now
kha sessions threads list "$SESSION_ID"
kha sessions threads get "$SESSION_ID" "$THREAD_ID"
kha sessions threads events "$SESSION_ID" "$THREAD_ID" --all -o json
kha sessions attach "$SESSION_ID" --thread "$THREAD_ID"
kha sessions fs list "$SESSION_ID" --prefix output
kha sessions fs download "$SESSION_ID" output/report.md --out report.md
```

- 运行之前可先 attach；查看 Session 是否真的从 `idle` → `running` → `idle`，确认是否存在 `requires_action`。
- `attach` 实时输出与 `events` 历史列表不同；断线保存 SSE `id` 游标，不是内嵌 KHA 事件对象 ID；可用 `--since "$SSE_CURSOR"` 续读。
- Child Thread 事件要用 `threads events` 单独获取；会话级只覆盖 Coordinator 视角。
- 文件列表 `fs list` 返回当前目录**直接子项**，不是递归；下载时用返回的真实 `path`，避免假设文件名称。
- 会话文件可能不完全持久；需要稳定的正式交付时，让云端 Agent 调用 `save_artifact`，具体独立 Artifact 接口和 CLI 用法务必通过 `kha docs` 校验。

## 上传必要文件（可外发且经授权）

```bash
kha files upload --file input.pdf --purpose file-extract -o json
```

该命令返回 `file_...` 等信息；确认文件 `extract_status`，在创建 Session 时用完整 JSON `resources: [{"type":"file","file_id":"..."}]` 绑定。上传不会自动绑定；`purpose=batch` 不能用于会话。禁止上传敏感资料。

## 异常处理及销毁边界

```bash
kha sessions interrupt "$SESSION_ID"   # 仅 running 当前轮次；不归档 Session
kha sessions archive "$SESSION_ID"     # 不可逆，必须明确必要性和授权
kha sessions delete "$SESSION_ID"      # 仅已归档会话；永久删除，需单独授权
```

- `kha agents update` / `kha environments update` 可能改变后续 Session 使用的配置，且集合字段可能整体替换；操作前先读现有配置，保留原字段。
- CLI 不支持或返回未知参数：先 `kha docs`，再查官方文档与 API。不要臆造新命令、不要绕过用户的网络/权限限制切换 API。

## Windows PowerShell

以上 `$VAR` 和 Here Document 示例是 POSIX Shell 语法。Windows 请将 JSON 存入文件，使用 `kha ... --file .\\coordinator.json` 等写法；在 PowerShell 中使用 `$env:VAR`（环境变量）或普通 `$VAR`（PowerShell 变量）读取真实 ID，不直接粘贴 Bash `<<'JSON'`。

