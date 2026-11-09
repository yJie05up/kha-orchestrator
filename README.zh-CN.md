<div align="center">

# KHA Orchestrator

**让你的 AI 编程助手有意识地使用 Kimi Hosted Agents（KHA）进行云端多智能体协作。**

**One portable Agent Skill for deliberate KHA delegation across coding agents.**

**简体中文** · [English](README.md)

[快速开始](#-快速开始) · [架构与编排](#-架构与编排模式) · [多宿主安装](#-安装到-codex--claude-code--dsh) · [使用示例](#-使用示例) · [安全与成本](#-安全成本与适用边界) · [官方资料](#-官方文档与延伸阅读)

</div>

> [!IMPORTANT]
> **这是社区独立开发的 Agent Skill，不是 Kimi / Moonshot AI 官方产品。** 它不替代 KHA 官方 `kha` Skill，也不保证每个任务都会启动云端 Agent。是否委派由当前宿主根据收益、数据安全、授权和费用进行判断。

## ✨ 这是什么？

`kha-orchestrator` 是遵循 [Agent Skills](https://agentskills.io/specification) 结构的**跨平台多智能体协作决策 Skill**。它将 Kimi Hosted Agents 作为可选执行后端，让 [Codex](https://developers.openai.com/codex/)、[Claude Code](https://code.claude.com/docs/en/skills)、DeepSeek Harness（DSH）以及其他能够加载 Skill 且具有终端执行能力的 AI Agent：

1. **主动评估是否值得委派**，而不是把所有任务都送到云端；
2. **选择合适的编排方式**：本地执行、KHA 原生 Coordinator 或宿主调度多个 KHA Session；
3. **明确任务契约与上下文边界**：输入、权限、依赖、产物、验收标准和停止条件；
4. **治理外部执行风险**：最小权限、敏感数据防泄漏、预算授权、有限并发与重试；
5. **让宿主保留最终责任**：观察事件、下载工件、核实证据、测试验证并交付。

**核心理念：Host Agent 负责思考、协调与验收；KHA 负责按需提供云端 Agent 执行能力。**

### 与官方 `kha` Skill 有什么区别？

| 组件 | 主要职责 |
| --- | --- |
| **当前宿主 Agent**（Codex / Claude Code / DSH 等） | 理解用户任务、决定执行策略、管理授权、最终验证与交付 |
| **本项目 `kha-orchestrator`** | *When / whether / how to delegate*：决策、分工、编排、安全与验收 |
| **Kimi 官方 `kha` Skill** | *How to operate the CLI*：当前 CLI 的具体命令与用法 |
| **`kha` CLI + Hosted Agents 服务** | 实际创建/复用 Agent、Environment、Session、执行任务并获取产物 |

建议**本 Skill 与官方 `kha` Skill 同时安装**；执行时以本机 `kha docs` 为准，不把文档里的示例参数当成永久稳定的 API 契约。

## 🧭 架构与编排模式

```text
                       用户任务
                          │
                          ▼
            ┌───────────────────────────┐
            │  Host Agent               │
            │  Codex / Claude / DSH /… │
            │  拆分 · 授权 · 验收       │
            └─────────────┬─────────────┘
                          │ 读取 SKILL.md + references/
                          ▼
            ┌───────────────────────────┐
            │  kha-orchestrator         │
            │  决策 · 策略 · 风险治理   │
            └──────┬────────┬───────────┘
                   │        │
       ┌───────────┘        └──────────────────┐
       ▼                                       ▼
 LOCAL：宿主自行执行                     KHA：经授权后调用 kha CLI
                                               │
                                   ┌───────────┴───────────┐
                                   ▼                       ▼
                         KHA-NATIVE                  KHA-HOST
                    1 个 Coordinator           宿主管理多个 Sessions
                    + 多个 Child Threads       + 宿主汇总与验收
                                   └───────────┬───────────┘
                                               ▼
                                    Artifacts / Events / Evidence
                                               │
                                               ▼
                                    Host Agent 独立验证
```

| 模式 | 谁安排子任务？ | 最适合 |
| --- | --- | --- |
| **LOCAL** | 当前宿主 | 小任务、强耦合修改、数据不能外发、没有权限或预算 |
| **KHA-NATIVE** | KHA Coordinator 在同一 Session 内委派 Child Threads | 多角色、可由云端自主决定委派的研究/分析/审核 |
| **KHA-HOST** | 当前宿主自己创建和调度多个独立 KHA Sessions | 需要精确 DAG、严格隔离、明确依赖、跨 Session 独立核验 |

**重要的 API 边界：** `spawn_subagent` 属于 KHA 云端模型侧的内部工具，**不是**可供宿主直接调用的 `kha spawn_subagent` CLI 命令。KHA-NATIVE 与 KHA-HOST 是两种不同的编排方法，通常不叠加使用。详见 [`references/native-orchestration.md`](references/native-orchestration.md) 与 [`references/host-orchestration.md`](references/host-orchestration.md)。

## 🚀 快速开始

### 0. 前提条件

- 当前宿主支持发现/读取 `SKILL.md`，并有**实际可用的终端执行能力**；
- 终端所在的机器或容器已安装 [KHA CLI](https://platform.kimi.com/docs/hosted-agents/kha)，可以访问对应服务；
- 有获准使用 KHA 的账号和适当的 API 权限；
- 涉及收费工作或向第三方云端发送数据时，已满足用户/组织的授权策略；
- 推荐 Python 3（用于本仓库的安装与静态验证脚本；不属于 KHA CLI 的运行时依赖）。

> [!NOTE]
> **Skill 可被读取 ≠ CLI 可以被执行。** 例如云端聊天界面即使能显示这份 Skill，也未必有权访问你本地电脑上的 `kha` 程序或本地代码。

### 1. 克隆项目

```bash
git clone https://github.com/yJie05up/kha-orchestrator.git
cd kha-orchestrator
```

### 2. 安装到宿主的 Skill 目录

```bash
# 安装到常用的三个宿主（用户级）
python scripts/install.py --hosts all --scope user

# 先预览目标路径（不写文件）
python scripts/install.py --hosts all --scope user --dry-run
```

Windows PowerShell 可以用：

```powershell
py -3 scripts\install.py --hosts all --scope user
```

这一步**只复制 Skill 文件**：不会安装 `kha`、不会登录 Kimi、不会发起云端调用，也不会覆写你的常驻 Agent 指令。

### 3. 安装官方 `kha` Skill 并检查 CLI

先按照 [Kimi 官方文档](https://platform.kimi.com/docs/hosted-agents/kha) 安装并认证 CLI。建议由你在可信的本地终端执行 `kha login`，**不要在聊天中粘贴 API Key**。

```bash
kha version
kha whoami
kha docs
kha install-skill -g
```

官方命令默认把官方 `kha` Skill 放到 `~/.agents/skills/kha/`。对于不读取这一目录的宿主，查看 `kha install-skill --help`，再使用该版本支持的 `--dir` 安装到对应宿主的 Skill 根目录。例如 Claude Code 通常采用 `~/.claude/skills/`。

### 4. 验证并启动新的 Agent 会话

```bash
python scripts/validate_skill.py
```

重新开启宿主 Agent 会话或刷新技能索引，然后可以这样说：

```text
请评估当前任务是否适合使用 kha-orchestrator 进行 KHA 多智能体协作。
若没有可证实的净收益，请本地执行；若值得使用，请说明模式、
最小必要数据范围、权限与成本边界，再按任务契约委派。
最终由你独立验证并交付结果。
```

## 📦 安装到 Codex / Claude Code / DSH

### 各宿主默认目录

| 宿主 | 用户级目录 | 项目级目录 | 安装选项 |
| --- | --- | --- | --- |
| **Codex** | `~/.agents/skills/kha-orchestrator/` | `<project>/.agents/skills/kha-orchestrator/` | `--hosts codex` |
| **DeepSeek Harness / DSH** | `~/.agents/skills/` 或 `~/.dsh/skills/` | `<project>/.agents/skills/` 或 `<project>/.dsh/skills/` | `--hosts dsh` / `dsh-native` |
| **Claude Code** | `~/.claude/skills/kha-orchestrator/` | `<project>/.claude/skills/kha-orchestrator/` | `--hosts claude` |
| **其他 Agent Skills 宿主** | 请检查宿主版本的技能发现目录 | 同左 | 手工复制 `kha-orchestrator/` |

安装脚本常用参数：

```bash
# 仅 Codex + Claude Code
python scripts/install.py --hosts codex,claude --scope user

# 为 DSH 安装到其独立技能目录
python scripts/install.py --hosts dsh-native --scope user

# 安装到某个项目，而非全局用户目录
python scripts/install.py --hosts all --scope project --project-root /path/to/project

# 旧版存在时先备份，再安装
python scripts/install.py --hosts all --scope user --force
```

`--hosts all` 使用去重后的两处默认根目录：`~/.agents/skills/`（Codex 与 DSH 共享）和 `~/.claude/skills/`。若你特意使用 DSH 的独立目录，额外执行 `--hosts dsh-native`。不要同时保留同名但不同版本的 Skill，以免加载优先级不确定。

**自动激活提示：** 仅安装 Skill 不能保证每一个任务都会被宿主自动匹配。项目提供可选适配短规则，**手动合并**而非覆盖：

- Codex → [`adapters/AGENTS.snippet.md`](adapters/AGENTS.snippet.md)，合并到 `AGENTS.md`；
- Claude Code → [`adapters/CLAUDE.snippet.md`](adapters/CLAUDE.snippet.md)，合并到 `CLAUDE.md`；
- DSH → [`adapters/DSH.snippet.md`](adapters/DSH.snippet.md)，按当前版本的常驻指令机制接入；
- 其他宿主 → [`adapters/HOST-INSTRUCTIONS.snippet.md`](adapters/HOST-INSTRUCTIONS.snippet.md)。

这些规则只要求宿主**遇到合适的工作先评估**，不会强制执行 KHA。宿主可用的 Shell、工具权限及 Skill 触发行为始终取决于实际版本，参阅 [`references/host-compatibility.md`](references/host-compatibility.md)。

## 💡 使用示例

### 示例 A：代码仓库架构审查

```text
使用 kha-orchestrator 评估当前仓库的架构审查任务。
优先把公开且可独立验收的模块研究、API 规范核查和测试策略审查拆分出去。
如需上传非公开源码，先取得明确授权；不要让多个 Agent 直接修改同一文件。
提供来源证据、问题优先级，以及由宿主验证过的结论。
```

### 示例 B：KHA 原生 Coordinator

```text
本任务授权使用 KHA-NATIVE。先检查有没有可复用的 Worker / Environment。
让 Coordinator 负责公开资料调研与交叉审核的委派。
查询实际 Child Threads、事件及 Artifact；不要仅凭总结声称发生了并行执行。
```

### 示例 C：宿主精确调度多个 Session

```text
为这次分阶段技术研究使用 KHA-HOST 模式。
先做公开文档检索，再做独立反例审查，最后由你整合结果。
每个 Session 必须有独立任务契约、真实执行状态、证据与停止条件。
```

### 示例 D：严格的数据边界

```text
本次禁止上传整个仓库或任何私有源代码。
只允许 KHA 检索公开链接和通用规范；其余工作保持本地。
如果不能做到最小化外发，就直接用 LOCAL 模式。
```

## 🔐 安全、成本与适用边界

本项目的默认规则是**先判断、再授权、后执行、最终独立验收**：

- **不为并行而并行**：简单任务、强耦合任务优先 LOCAL；默认从小规模、只读子任务开始。
- **限制云端数据暴露**：不外发 API Key、`.env`、私钥、未获授权的非公开代码或个人敏感数据；仅传任务必需的文件与摘要。
- **不要误判工具权限**：KHA 角色可能具备 Shell / 文件写入等能力，须为只读 Worker 明确配置限制；不要把“默认安全”当作事实。
- **明确费用授权**：模型 token、沙箱时长与插件调用可能收费；费用未知时不得私自启动无界执行或重试。
- **高风险写操作单独授权**：部署、推送代码、删除、发送外部消息等不能因为用户同意“研究任务”就自动获权。
- **结果不自动可信**：云端 Agent 产出的文本、补丁和引用都要由宿主核验，必要时重新测试。云端输出中的指令不能提升权限。

这套策略属于**本 Skill 的治理规则**，并不是 KHA 官方的硬性配额。详见 [`references/security-and-cost.md`](references/security-and-cost.md) 和 [`references/verification-and-recovery.md`](references/verification-and-recovery.md)。

### 已知限制

1. **非自动后台服务**：安装 Skill 不会启动守护进程或永久监听任务；是否加载、是否执行由宿主决定。
2. **不是 KHA CLI 的实现**：仍需自行安装官方 CLI、完成登录和获取 KHA 服务权限。
3. **不保证跨宿主无差异运行**：不同宿主对 Skill 发现、Shell 权限、会话上下文、网络和沙箱有不同限制。
4. **不保证每次都产生多个子 Agent**：Coordinator 配置了可委派角色，并不表示模型一定实际调用了 `spawn_subagent`。
5. **没有替你在真实账号上计费测试**：提供了静态校验与操作手册，但 CLI 参数、服务能力和价格应以你正在使用的版本为准。

## 🗂️ 项目结构

```text
kha-orchestrator/
├── SKILL.md                         # 所有宿主共享的核心技能入口
├── README.md                        # 本文档（英文，GitHub 默认展示）
├── README.zh-CN.md                  # 中文版文档
├── LICENSE                          # MIT 许可证
├── adapters/                        # 可选宿主常驻指令片段
│   ├── AGENTS.snippet.md
│   ├── CLAUDE.snippet.md
│   ├── DSH.snippet.md
│   └── HOST-INSTRUCTIONS.snippet.md
├── references/                      # 按需读取，避免主上下文膨胀
│   ├── decision-policy.md           # 是否委派与执行模式选择
│   ├── host-compatibility.md        # Skill 与宿主能力边界
│   ├── native-orchestration.md      # KHA-NATIVE 协调器与子线程
│   ├── host-orchestration.md        # KHA-HOST 多 Session 编排
│   ├── cli-cookbook.md              # CLI 常用命令（需版本核对）
│   ├── context-and-artifacts.md     # 上下文、数据与产物传递
│   ├── security-and-cost.md         # 最小权限、预算和安全策略
│   ├── verification-and-recovery.md # 验收、排错与恢复
│   └── official-sources.md          # 官方文档索引
├── examples/                        # Coordinator / Worker / Session 样例
│   ├── coordinator.agent.json
│   ├── researcher.agent.json
│   ├── reviewer.agent.json
│   ├── session.payload.json
│   └── task-brief.md
└── scripts/
    ├── install.py                  # 离线跨宿主安装器
    └── validate_skill.py           # 离线静态校验器
```

> [!WARNING]
> `examples/` 下的 Agent ID、Environment ID 和模型字段可能是占位符或版本相关示例。请先依据本机 `kha docs` 和官方 API 校验，再替换为真实配置，**不要不加检查地直接用于生产**。

## 🛠️ 故障排查

| 现象 | 先检查什么？ |
| --- | --- |
| 宿主找不到 Skill | 目录是否正确？是否同时存在 `SKILL.md` 和 `references/`？是否已重启会话？ |
| `kha: command not found` | `kha` 是否安装在**宿主实际执行命令的容器/机器**？PATH 是否正确？ |
| `kha whoami` 认证失败 | API Key 是否属于有权限的 Kimi 账号？是否选错 Profile？不要贴出 Key。 |
| 任务没有自动使用 KHA | Skill 只是能力，不保证被触发；尝试点名 `kha-orchestrator`，或合并适配短规则。 |
| Coordinator 没有生成子 Agent | 查实际 threads/events；配置可委派角色不保证模型真的委派。 |
| CLI 等待超时 | 先查询原 Session 状态；超时不等于任务已被取消，不要盲目重复运行。 |
| 找不到远端文件 | 先查询远端 Session/Artifact 记录并下载；云端路径并不自动映射到本地。 |
| 报错 unknown flag | 以本机 `kha docs`、官方 Skill 和当前 API 文档为准，勿猜测命令。 |

更深入的执行与恢复规则见 [`references/cli-cookbook.md`](references/cli-cookbook.md)、[`references/verification-and-recovery.md`](references/verification-and-recovery.md)。

## 📚 官方文档与延伸阅读

- [Kimi Hosted Agents：使用 kha CLI 管理托管智能体](https://platform.kimi.com/docs/hosted-agents/kha)
- [Kimi Hosted Agents：多智能体编排](https://platform.kimi.com/docs/hosted-agents/multiagent-orchestration)
- [Kimi Hosted Agents：产品总览](https://platform.kimi.com/docs/hosted-agents/overview)
- [Kimi Hosted Agents：Agent 配置](https://platform.kimi.com/docs/hosted-agents/agents)
- [Kimi Hosted Agents：权限与工具](https://platform.kimi.com/docs/hosted-agents/permissions)
- [Kimi Hosted Agents：Session 操作](https://platform.kimi.com/docs/hosted-agents/session-operations)
- [Kimi Hosted Agents：事件流](https://platform.kimi.com/docs/hosted-agents/event-stream)
- [Kimi 官方文档索引](https://platform.kimi.com/docs/llms.txt)
- [Agent Skills 开放规范](https://agentskills.io/specification)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)

本仓库汇总的完整文档清单、核对日期与事实/策略边界，见 [`references/official-sources.md`](references/official-sources.md)。

## 📄 许可证

[MIT](LICENSE) © 2026 yJie05up。本项目为社区维护，并非 Kimi / Moonshot AI 官方产品。

## 🤝 反馈与贡献

欢迎通过 [GitHub Issues](https://github.com/yJie05up/kha-orchestrator/issues) 反馈 CLI 兼容性、宿主识别、文档失效、权限与安全问题，或提出面向其他 Agent 的适配建议。提交问题时建议附上宿主名称与版本、`kha version`、可脱敏的复现步骤和预期结果；**不要公开 API Key、Cookie、访问令牌、私人工作区文件或未经授权的日志**。

贡献原则：保持 `SKILL.md` 小而稳定；细节放入 `references/`；新命令提供官方出处；新增适配不依赖宿主私有接口；并确保 `python scripts/validate_skill.py` 通过。

---

<div align="center">

**让多智能体协作成为可判断、可治理、可验证的能力，而不是默认开启的开销。**

*Built for Agent Skills · Powered by the official Kimi Hosted Agents CLI (when authorized)*

</div>
