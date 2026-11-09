# 官方资料索引与事实边界

访问核对日期：2026-11-09。KHA 仍处 Beta/迭代阶段，运行命令以所在机器 `kha docs` 优先。

## Kimi Hosted Agents

- 主索引：https://platform.kimi.com/docs/llms.txt
- CLI：https://platform.kimi.com/docs/hosted-agents/kha
- 多智能体：https://platform.kimi.com/docs/hosted-agents/multiagent-orchestration
- 产品概览：https://platform.kimi.com/docs/hosted-agents/overview
- 快速开始：https://platform.kimi.com/docs/hosted-agents/quickstart
- Agents：https://platform.kimi.com/docs/hosted-agents/agents
- Permissions：https://platform.kimi.com/docs/hosted-agents/permissions
- Tools：https://platform.kimi.com/docs/hosted-agents/tools
- Environments：https://platform.kimi.com/docs/hosted-agents/environments
- Sessions：https://platform.kimi.com/docs/hosted-agents/sessions
- Session operations：https://platform.kimi.com/docs/hosted-agents/session-operations
- Events：https://platform.kimi.com/docs/hosted-agents/event-stream
- Files：https://platform.kimi.com/docs/hosted-agents/files
- Skills：https://platform.kimi.com/docs/hosted-agents/skills
- Plugins：https://platform.kimi.com/docs/hosted-agents/plugins
- MCP：https://platform.kimi.com/docs/hosted-agents/mcp
- Vault：https://platform.kimi.com/docs/hosted-agents/vaults
- Memory：https://platform.kimi.com/docs/hosted-agents/memory
- Self-hosted：https://platform.kimi.com/docs/hosted-agents/self-hosted-environments
- Triggers：https://platform.kimi.com/docs/hosted-agents/triggers
- FAQ：https://platform.kimi.com/docs/hosted-agents/faq
- Changelog：https://platform.kimi.com/docs/hosted-agents/changelog
- OpenAPI：https://platform.kimi.com/docs/hosted-agents/openapi.yaml

## 官方多智能体案例

- SRE：https://platform.kimi.com/docs/hosted-agents/official-sre-incident-agent
- 投资研究：https://platform.kimi.com/docs/hosted-agents/official-investment-research-agent
- 基金对账：https://platform.kimi.com/docs/hosted-agents/official-fund-reconciliation-agent

## 跨宿主技能规范

- Agent Skills 规范：https://agentskills.io/specification
- Codex 路径：https://developers.openai.com/api/reference/cli
- Claude Code：https://code.claude.com/docs/en/skills
- DSH Skill Provider：https://omdsh.agi.fans/docs/skills-and-mcp/
- dsh-cc：https://dsh-cc.github.io/guide/skills

## 区分平台事实与本 Skill 策略

**平台事实**：KHA 支持 `multiagent.agents`、Coordinator/Child Threads；模型在运行时调用 `spawn_subagent`，不是客户端直接发起的 CLI/REST 命令；Session 与 Environment 有版本/状态约束；宿主可通过 CLI 查事件和下载文件。**本 Skill 自定**：评分策略、默认 2 个 Worker、首次计费授权门槛、任务契约、低成本优先及结果审计格式等。不要误称为官方配额或 API 字段。静态文档核对不是用户账户上的端到端测试。

