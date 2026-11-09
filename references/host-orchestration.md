# 宿主显式编排多个 Session（KHA-HOST）

官方基础：https://platform.kimi.com/docs/hosted-agents/sessions 、 https://platform.kimi.com/docs/hosted-agents/environments

## 任务 DAG

建立任务账本：`task_id | owner | inputs | dependencies | status | session_id | acceptance | output`。

- Wave 0：宿主 评估输入和权限，确定并发任务数。
- Wave 1：相互独立的只读调研/审查/分析，分别创建 Session，绑定各自 Agent/Environment。资源和身份按最小权限隔离。
- Wave 2：宿主 收集结果并与本地事实比对；冲突时单独复查或发送追问（不要无限自激重试）。
- Wave 3：需要将 Wave 1 结果送给下一轮 Agent 时，显式把已经检查/脱敏的必要数据作为新消息或上传文件绑定；不同 Session **不共享** 沙箱、文件、进程或完整模型上下文。
- Wave 4：所有结果由 宿主 验收；本地代码应用、测试、构建、提交仍由 宿主 控制。

## 示例（非自动运行脚本）

```bash
# 所有 ID 来自真实响应；不要复制占位符运行
kha sessions create --agent "$REVIEW_AGENT_ID" --environment "$READY_ENV_ID" --title "API review"
kha sessions create --agent "$RESEARCH_AGENT_ID" --environment "$READY_ENV_ID" --title "SDK study"
# 对各自返回的 Session ID 单独发送：
kha sessions send "$REVIEW_SESSION_ID" "只读审查公开的 API 设计资料，列出严重性、证据和建议，不修改任何外部资源。"
kha sessions send "$RESEARCH_SESSION_ID" "研究指定公共 SDK，记录可核验的版本、引用和兼容性约束。"
```

**重要**：Session 创建后处于 `idle`，必须 `send` 才会开始。系统不保证 CLI 本地等待与云端运行同步结束。

## 并发与冲突

- 起步少量并行，优先使用明确 IO 边界的任务；预算未知不爆发式新建会话。
- 每个 Session 的工件保存时采用任务 ID 命名并检查来源，文件下载到隔离目录，不直接覆盖项目文件。
- `idle` 不必然成功；要确认 `stop_reason`、`session.error`、必要的工具结果和产物。
- 失败不盲目重试 `create` 以免重复消耗；先查询此前拿到的 Session ID。
- 若涉及相同源码的改写，优先让各 Agent 输出 **建议 patch 文本**，由 宿主统一应用/冲突解决；不要让多个云端会话同时写同一分支。

## 选择从 CLIENT 降级的条件

当需要提交的上下文过于敏感、Agent 缺少工具/网络/依赖、预算失控、无可验证产物、云端运行错误未能在合理次数恢复时，停止继续创建远端 Session，保留已获结果，改回本地流程并真实报告未完成部分。

