# KHA 原生多智能体（KHA-NATIVE）：宿主无关

官方权威：https://platform.kimi.com/docs/hosted-agents/multiagent-orchestration

## 资源与通信约束

- 先创建/复用普通 Worker Agents，再创建 Coordinator Agent；`multiagent: {"type":"coordinator", "agents":[...]}`。
- 委派条目 `{ "type":"agent", "id":"真实AgentID", "version":"可选精确版本" }`，或 `{ "type":"self" }`。必须 1–20 个条目；禁止引用已归档 Agent、显示名重复、重复同一 Agent 或另一个 Coordinator。
- Coordinator 的模型会选择委派名单中的 Agent，调用内部 `spawn_subagent` 创建同 Session 的 Child Thread。`spawn_subagent` 不属于 CLI/HTTP 的客户端 API。
- `spawn_subagent` 模型侧主要参数：`agent_type`（委派对象显示名，必填）、`description`、`prompt`、`run_in_background`。默认同步，true 异步；这是解释模型行为的契约，不是供 宿主 调用的 CLI 命令。
- 异步线程可保留 `idle` 并由 Coordinator 使用 `send_message` 再委派；`wait_for_message` 和 `delete_subagent` 亦是模型侧工具。子线程不能创建孙线程；子线程只能向 Coordinator 发消息，不能直接跨子线程/跨会话。客户端不能直接向 child thread 发送消息。
- 会话级 `agent_overrides` 仅作用 Coordinator，不自动影响 Worker；子 Agent 按委派时锁定的配置运行。
- Cloud Session 多个 Thread 属于同一会话，**共享执行环境不等于共享模型上下文**。关于工作目录并发冲突，不假设安全；同文件并行写入要避免，最好采用只读任务、独立文件名和最终 宿主 检查。

## 推荐 Coordinator system 指令骨架

> 你负责把输入任务拆成可以独立验证的最少子任务。只给已配置的 Agent 委派适配其能力的任务。子任务 prompt 必须写清输入、输出、证据、成功条件、错误处理、文件命名和只读/可写边界。可并行且互不依赖时才使用异步委派。等待需要的报告后，对事实交叉复核，列出分歧与待验证项。不要调用不存在的 CLI 或让子代理访问不可用的本地文件。不得声称已完成未发生的测试或工具调用。最终报告包括结论、引用证据、失败/不足、产物路径、每个子任务结果；没有用户明确权限时不进行外部状态修改。

## 宿主的执行顺序

1. `kha whoami`，查询当前资源。只在缺少合适 Worker 时创建 Worker Agent。Agent 名称必须唯一且易于作为 `agent_type` 显示名引用；创建时保存真实 ID。
2. 创建 Coordinator，`multiagent.agents` 中填实际 Worker ID；可参考 `examples/coordinator.agent.json`，**先替换占位符**。
3. 准备 ready Environment，创建 Session，记录返回的 `sesn_...` ID。
4. 先 attach，再 `kha sessions send SESSION_ID "任务..."`，可在提示中要求 Coordinator 并行委派、按固定格式汇总。
5. 使用 `kha sessions threads list SESSION_ID` 获取 `sthr_...` ID，检查是否真的生成 Child Threads；没有生成则不要宣称运行了多个 Agent。
6. 对重要线程使用 `kha sessions threads events SESSION_ID THREAD_ID --all -o json`，区分实际工具操作/模型文字；检查最终 Session 是否结束该轮并提供工件。
7. 宿主本地复核后输出。

## 常见误区

- 配置多 Agent 只声明允许委派，**不保证这次任务会真正 spawn**。
- `spawn_subagent` 参数是模型内部调用输入，不要生成 `kha spawn_subagent ...` 命令。
- 往 Coordinator 发消息不等于直接给 Child Thread 发消息。
- Agent 更新会创建新版本，已有 Session 不受影响；已保存 Coordinator 的委派列表也会固定所引用 Worker 版本，必要时更新 Coordinator 并新建 Session。
- 需要客户端严格保证子任务数目、顺序或 DAG → 改选 KHA-HOST。

