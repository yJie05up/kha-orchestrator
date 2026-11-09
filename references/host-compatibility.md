# 宿主兼容性与能力分层

## 标准与最低条件

采用 [Agent Skills](https://agentskills.io/specification) 的核心交集：目录 `kha-orchestrator/SKILL.md`、YAML frontmatter 的 `name`、`description`、普通 Markdown 和相对路径 references。**无专有 hooks、agent 字段、shell 工具名、MCP server 依赖**。`compatibility`/`metadata` 是标准可选项；极少数旧版解析器若不接受，可删除可选 frontmatter，但不要破坏必选 `name`/`description`。

执行有四层不同的能力，不可混为一谈：

1. **发现**：能否扫描 Skill 目录并列出技能。
2. **加载**：能否读取 `SKILL.md` 和引用的相对路径文档。
3. **执行**：Agent 是否具有合适的终端/进程调用工具并能找到 `kha` 二进制。
4. **连接**：该执行容器/系统是否允许连接 KHA API、持有合法授权且可以承担费用。

仅满足前两项是“说明文档可读”，不代表能运行 KHA。

## 当前核对的目录

| Host | Project root | User root | Notes |
|---|---|---|---|
| Codex | `.agents/skills/kha-orchestrator` | `~/.agents/skills/kha-orchestrator` | 用户可通过 AGENTS.md 短规则提高评估频率 |
| DeepSeek Harness / DSH | `.agents/skills/kha-orchestrator` 或 `.dsh/skills/kha-orchestrator` | `~/.agents/skills/kha-orchestrator` 或 `~/.dsh/skills/kha-orchestrator` | 具体 dsh preset 和 provider 可能改变优先级 |
| Claude Code (local) | `.claude/skills/kha-orchestrator` | `~/.claude/skills/kha-orchestrator` | 本机 Claude Code 与 Claude 云端聊天的文件系统不通用 |
| Other hosts | 查其官方 Skill discovery paths | 同左 | 若不兼容 Agent Skills，则需人工/适配层读取正文 |

## 官方 kha Skill 需要单独处理

`kha install-skill -g` 的默认根目录 `~/.agents/skills/kha/` 对 Codex/DSH 常见配置可见，但**Claude Code 默认不扫描这个目录**。在 Claude Code 上，使用 `kha install-skill --dir` 将官方 `kha` 包安装到 `~/.claude/skills` 或让其读取相应文档；先通过本机 `kha install-skill --help` 检查 `--dir` 参数含义。两个技能目录分别为 `kha/` 与 `kha-orchestrator/`，不能相互覆盖。

## 激活与优先级

- 各宿主的自动触发都依赖描述匹配、会话上下文与宿主版本，**不能保证“每个任务都提醒自己”**。
- 需更多主动性时，在宿主的常驻指令里添加一条“遇到合适的复杂任务先评估 kha-orchestrator”，不是“一定要执行”。参阅 `adapters/`。
- 受更高优先级用户/系统规则、无网络、安全沙箱、组织政策限制时，本 Skill 不能越权调用 CLI。
- `.agents/skills` 与 `.dsh/skills` 同名部署时可能发生优先级覆盖；优先部署**同一版本的一份**，减少漂移。

## 已核对文档

- https://agentskills.io/specification
- https://developers.openai.com/api/reference/cli
- https://code.claude.com/docs/en/skills
- https://omdsh.agi.fans/docs/skills-and-mcp/
- https://dsh-cc.github.io/guide/skills

