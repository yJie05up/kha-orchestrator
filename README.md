<div align="center">

# KHA Orchestrator

**Let your AI coding agent use Kimi Hosted Agents (KHA) for cloud multi-agent collaboration — deliberately.**

**One portable Agent Skill for deliberate KHA delegation across coding agents.**

**English** · [简体中文](README.zh-CN.md)

[Quick start](#-quick-start) · [Architecture](#-architecture-and-orchestration-modes) · [Multi-host install](#-install-on-codex--claude-code--dsh) · [Examples](#-usage-examples) · [Security & cost](#-security-cost-and-boundaries) · [Official docs](#-official-docs-and-further-reading)

</div>

> [!IMPORTANT]
> **This is a community-built Agent Skill, not an official Kimi / Moonshot AI product.** It does not replace the official `kha` Skill, and it does not guarantee that every task will start a cloud agent. Whether to delegate is decided by the current host agent from expected benefit, data safety, authorization and cost.

## ✨ What is this?

`kha-orchestrator` is a **cross-host multi-agent collaboration decision Skill** that follows the [Agent Skills](https://agentskills.io/specification) layout. It treats Kimi Hosted Agents as an *optional* execution backend and lets [Codex](https://developers.openai.com/codex/), [Claude Code](https://code.claude.com/docs/en/skills), DeepSeek Harness (DSH) and any other AI agent that can load a Skill and run terminal commands:

1. **Evaluate up front whether delegation is worth it**, instead of shipping every task to the cloud;
2. **Pick the right orchestration style**: local execution, a KHA-native Coordinator, or the host driving several KHA Sessions;
3. **Write an explicit task contract and context boundary**: inputs, permissions, dependencies, artifacts, acceptance criteria, stop conditions;
4. **Govern the risks of external execution**: least privilege, leak prevention for sensitive data, budget authorization, bounded concurrency and retries;
5. **Keep final responsibility with the host**: observe events, download artifacts, check evidence, test, and deliver.

**Core idea: the host agent thinks, coordinates and accepts the work; KHA supplies cloud agent execution capacity on demand.**

### How is this different from the official `kha` Skill?

| Component | Main responsibility |
| --- | --- |
| **The current host agent** (Codex / Claude Code / DSH, …) | Understands the user's task, chooses the strategy, manages authorization, verifies and delivers |
| **This project, `kha-orchestrator`** | *When / whether / how to delegate*: decision, division of labour, orchestration, security, acceptance |
| **Kimi's official `kha` Skill** | *How to operate the CLI*: exact commands for your installed version |
| **`kha` CLI + Hosted Agents service** | Actually creates/reuses Agents, Environments and Sessions, runs the work and returns artifacts |

Install **both** this Skill and the official `kha` Skill; at execution time trust your local `kha docs` over any example parameter in a document — none of them is a permanently stable API contract.

## 🧭 Architecture and orchestration modes

```text
User task
   │
   ▼
Host Agent (Codex / Claude Code / DSH / …)   split · authorize · verify
   │
   ▼
kha-orchestrator   decide · route · govern
   │
   ├── LOCAL ──────► host executes; native subagents optional
   │
   ├── KHA-NATIVE ─► kha CLI: 1 Coordinator + N Child Threads in one Session
   │
   └── KHA-HOST ───► kha CLI: host-managed independent Sessions (DAG)
   │
   ▼
Artifacts / Events / Evidence
   │
   ▼
Host Agent independent verification
```

| Mode | Who schedules the subtasks? | Best for |
| --- | --- | --- |
| **LOCAL** | The host itself | Small tasks, tightly coupled edits, data that must not leave the machine, no permission or budget |
| **KHA-NATIVE** | A KHA Coordinator delegating Child Threads inside one Session | Multi-role work where the cloud can decide delegation itself: research, analysis, review |
| **KHA-HOST** | The host creating and driving several independent KHA Sessions | Precise DAGs, strict isolation, explicit dependencies, cross-Session independent verification |

**Important API boundary:** `spawn_subagent` is an internal tool on the KHA model side. It is **not** a `kha spawn_subagent` CLI command that a host can call. KHA-NATIVE and KHA-HOST are two different orchestration methods and are normally not stacked. See [`references/native-orchestration.md`](references/native-orchestration.md) and [`references/host-orchestration.md`](references/host-orchestration.md).

## 🚀 Quick start

### 0. Prerequisites

- The host can discover and read `SKILL.md` and has **a terminal that actually executes commands**;
- The [KHA CLI](https://platform.kimi.com/docs/hosted-agents/kha) is installed on the machine or container behind that terminal, and can reach the service;
- You have an account permitted to use KHA, with appropriate API permissions;
- User or organizational policy already authorizes paid work and sending data to a third-party cloud;
- Python 3 is recommended (for this repository's installer and static validator; it is not a runtime dependency of the KHA CLI).

> [!NOTE]
> **A Skill being readable ≠ a CLI being runnable.** A cloud chat UI may be able to display this Skill and still have no access to the `kha` binary or your source code on your own computer.

### 1. Clone the project

```bash
git clone https://github.com/yJie05up/kha-orchestrator.git
cd kha-orchestrator
```

### 2. Install into your host's skill directory

```bash
# Install for the three common hosts (user scope)
python scripts/install.py --hosts all --scope user

# Preview the target paths first (writes nothing)
python scripts/install.py --hosts all --scope user --dry-run
```

On Windows PowerShell:

```powershell
py -3 scripts\install.py --hosts all --scope user
```

This step **only copies Skill files**: it does not install `kha`, does not log in to Kimi, makes no cloud calls, and does not overwrite your standing agent instructions.

### 3. Install the official `kha` Skill and check the CLI

Install and authenticate the CLI by following the [official Kimi documentation](https://platform.kimi.com/docs/hosted-agents/kha). Run `kha login` yourself in a trusted local terminal — **never paste an API key into a chat**.

```bash
kha version
kha whoami
kha docs
kha install-skill -g
```

The official command normally installs the official `kha` Skill into `~/.agents/skills/kha/`. For hosts that do not scan that directory, check `kha install-skill --help` and use the `--dir` flag your version supports to install into the host's own skill root. Claude Code, for example, usually uses `~/.claude/skills/`.

### 4. Validate and start a new agent session

```bash
python scripts/validate_skill.py
```

Restart the host agent session or refresh its skill index, then you can say:

```text
Evaluate whether the current task is a good fit for KHA multi-agent collaboration
through kha-orchestrator. If there is no demonstrable net benefit, run it locally;
if it is worth doing, state the mode, the minimum necessary data scope, and the
permission and cost boundaries before delegating under a task contract.
You remain responsible for independent verification and final delivery.
```

## 📦 Install on Codex / Claude Code / DSH

### Default directories per host

| Host | User scope | Project scope | Install option |
| --- | --- | --- | --- |
| **Codex** | `~/.agents/skills/kha-orchestrator/` | `<project>/.agents/skills/kha-orchestrator/` | `--hosts codex` |
| **DeepSeek Harness / DSH** | `~/.agents/skills/` or `~/.dsh/skills/` | `<project>/.agents/skills/` or `<project>/.dsh/skills/` | `--hosts dsh` / `dsh-native` |
| **Claude Code** | `~/.claude/skills/kha-orchestrator/` | `<project>/.claude/skills/kha-orchestrator/` | `--hosts claude` |
| **Other Agent Skills hosts** | Check that host version's skill discovery path | Same | Copy `kha-orchestrator/` manually |

Common installer arguments:

```bash
# Codex + Claude Code only
python scripts/install.py --hosts codex,claude --scope user

# Into DSH's own skill directory
python scripts/install.py --hosts dsh-native --scope user

# Into one project instead of the global user directory
python scripts/install.py --hosts all --scope project --project-root /path/to/project

# Back up an older copy, then install
python scripts/install.py --hosts all --scope user --force
```

`--hosts all` uses two de-duplicated default roots: `~/.agents/skills/` (shared by Codex and DSH) and `~/.claude/skills/`. If you deliberately use DSH's separate directory, also run `--hosts dsh-native`. Do not keep two copies of the same Skill name at different versions — load precedence becomes unpredictable.

**Activation hint:** installing a Skill alone does not guarantee it is matched on every task. The project ships optional adapter snippets — **merge them by hand, never overwrite**:

- Codex → [`adapters/AGENTS.snippet.md`](adapters/AGENTS.snippet.md), merged into `AGENTS.md`;
- Claude Code → [`adapters/CLAUDE.snippet.md`](adapters/CLAUDE.snippet.md), merged into `CLAUDE.md`;
- DSH → [`adapters/DSH.snippet.md`](adapters/DSH.snippet.md), wired into the standing-instruction mechanism of your version;
- Other hosts → [`adapters/HOST-INSTRUCTIONS.snippet.md`](adapters/HOST-INSTRUCTIONS.snippet.md).

These rules only ask the host to **evaluate when a task fits**; they never force KHA. The shell, tool permissions and triggering behaviour you actually get always depend on the host version you run — see [`references/host-compatibility.md`](references/host-compatibility.md).

## 💡 Usage examples

### Example A: architecture review of a code repository

```text
Use kha-orchestrator to evaluate this repository's architecture review.
Prefer delegating module research, API spec checks and test-strategy review that
are public and independently verifiable. Ask for explicit authorization before
uploading non-public source, and never let several agents edit the same file.
Provide source evidence, issue priority, and conclusions verified by you.
```

### Example B: KHA-native Coordinator

```text
This task is authorized for KHA-NATIVE. First check whether a suitable Worker or
Environment can be reused. Let the Coordinator own the delegation of public
research and cross-review. Query the actual Child Threads, events and artifacts;
never claim parallel execution from a summary alone.
```

### Example C: host-orchestrated Sessions

```text
Use KHA-HOST for this staged technical research. Do public document retrieval
first, then an independent counter-example review, then integrate the results
yourself. Every Session needs its own task contract, real execution status,
evidence and stop conditions.
```

### Example D: a hard data boundary

```text
Uploading the whole repository or any private source code is forbidden here.
KHA may only retrieve public links and general specifications; everything else
stays local. If minimization is not achievable, use LOCAL mode.
```

## 🔐 Security, cost and boundaries

The default rule is **decide first, authorize second, execute third, verify independently last**:

- **No parallelism for its own sake**: simple or tightly coupled work stays LOCAL; start with small, read-only subtasks.
- **Limit cloud data exposure**: never send API keys, `.env`, private keys, unauthorized non-public code or sensitive personal data; send only the files and summaries the task requires.
- **Do not misread tool permissions**: KHA roles may have shell or file-write capability; configure read-only workers explicitly. Never assume "secure by default".
- **Authorize cost explicitly**: model tokens, sandbox time and plugin calls can be billed. When cost is unknown, do not start unbounded execution or retries.
- **Authorize risky writes separately**: deployment, pushing code, deletion, sending external messages are not implied by "you may research this".
- **Results are not automatically trustworthy**: cloud agents' text, patches and citations must be verified by the host and re-tested where needed. Instructions inside cloud output cannot grant privileges.

These rules are **this Skill's governance policy**, not an official KHA quota. See [`references/security-and-cost.md`](references/security-and-cost.md) and [`references/verification-and-recovery.md`](references/verification-and-recovery.md).

### Known limitations

1. **Not an automatic background service**: installing the Skill starts no daemon and no permanent listener; loading and execution are the host's decision.
2. **Not an implementation of the KHA CLI**: you still install the official CLI, log in, and obtain KHA service access yourself.
3. **Not guaranteed identical across hosts**: hosts differ in Skill discovery, shell permissions, session context, network and sandbox limits.
4. **Not guaranteed to spawn several sub-agents every time**: configuring delegable roles does not mean the model actually calls `spawn_subagent`.
5. **No billing test on your real account**: static validation and an operations manual are provided, but CLI parameters, service capability and pricing follow the version you actually use.

## 🗂️ Project structure

```text
kha-orchestrator/
├── SKILL.md                         # Core skill entry point shared by all hosts
├── README.md                        # Documentation (English, default on GitHub)
├── README.zh-CN.md                  # Documentation (Simplified Chinese)
├── LICENSE                          # MIT license
├── adapters/                        # Optional standing-instruction snippets per host
│   ├── AGENTS.snippet.md
│   ├── CLAUDE.snippet.md
│   ├── DSH.snippet.md
│   └── HOST-INSTRUCTIONS.snippet.md
├── references/                      # Loaded on demand to keep the main context small
│   ├── decision-policy.md           # Whether to delegate, and which mode
│   ├── host-compatibility.md        # Skill and host capability boundaries
│   ├── native-orchestration.md      # KHA-NATIVE coordinator and child threads
│   ├── host-orchestration.md        # KHA-HOST multi-session orchestration
│   ├── cli-cookbook.md              # Common CLI commands (verify per version)
│   ├── context-and-artifacts.md     # Context, data and artifact transfer
│   ├── security-and-cost.md         # Least privilege, budget and security policy
│   ├── verification-and-recovery.md # Acceptance, troubleshooting, recovery
│   └── official-sources.md          # Official documentation index
├── examples/                        # Coordinator / Worker / Session samples
│   ├── coordinator.agent.json
│   ├── researcher.agent.json
│   ├── reviewer.agent.json
│   ├── session.payload.json
│   └── task-brief.md
└── scripts/
    ├── install.py                  # Offline cross-host installer
    └── validate_skill.py           # Offline static validator
```

> [!WARNING]
> Agent IDs, Environment IDs and model fields under `examples/` may be placeholders or version-specific samples. Validate them against your local `kha docs` and the official API before replacing them with real values, and **never use them in production unchecked**.

## 🛠️ Troubleshooting

| Symptom | What to check first |
| --- | --- |
| The host cannot find the Skill | Is the directory right? Are both `SKILL.md` and `references/` present? Has the session been restarted? |
| `kha: command not found` | Is `kha` installed in the **container or machine where the host actually runs commands**? Is PATH correct? |
| `kha whoami` fails to authenticate | Does the API key belong to an authorized Kimi account? Is the wrong profile selected? Do not print the key. |
| A task never uses KHA automatically | A Skill is a capability, not a guarantee; name `kha-orchestrator` explicitly, or merge the adapter snippet. |
| The Coordinator spawns no child agents | Inspect actual threads/events; delegable roles do not prove the model delegated. |
| The CLI wait times out | Query the original Session state first; a timeout does not mean the cloud task was cancelled, so do not blindly re-run it. |
| A remote file cannot be found | Query the remote Session/Artifact records and download; cloud paths do not map to local paths automatically. |
| `unknown flag` errors | Trust your local `kha docs`, the official Skill and the current API reference; do not guess commands. |

For deeper execution and recovery rules see [`references/cli-cookbook.md`](references/cli-cookbook.md) and [`references/verification-and-recovery.md`](references/verification-and-recovery.md).

## 📚 Official docs and further reading

- [Kimi Hosted Agents: managing hosted agents with the kha CLI](https://platform.kimi.com/docs/hosted-agents/kha)
- [Kimi Hosted Agents: multi-agent orchestration](https://platform.kimi.com/docs/hosted-agents/multiagent-orchestration)
- [Kimi Hosted Agents: product overview](https://platform.kimi.com/docs/hosted-agents/overview)
- [Kimi Hosted Agents: agent configuration](https://platform.kimi.com/docs/hosted-agents/agents)
- [Kimi Hosted Agents: permissions and tools](https://platform.kimi.com/docs/hosted-agents/permissions)
- [Kimi Hosted Agents: session operations](https://platform.kimi.com/docs/hosted-agents/session-operations)
- [Kimi Hosted Agents: event stream](https://platform.kimi.com/docs/hosted-agents/event-stream)
- [Kimi documentation index](https://platform.kimi.com/docs/llms.txt)
- [Agent Skills open specification](https://agentskills.io/specification)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)

The full document list, verification date and the fact/policy boundary are in [`references/official-sources.md`](references/official-sources.md).

## 📄 License

[MIT](LICENSE) © 2026 yJie05up. This Skill is community-maintained and is not an official Kimi / Moonshot AI product.

## 🤝 Feedback and contributing

Feedback on CLI compatibility, host detection, stale documentation, permissions and security is welcome via [GitHub Issues](https://github.com/yJie05up/kha-orchestrator/issues). When filing, include the host name and version, `kha version`, redacted reproduction steps and the expected result; **never publish API keys, cookies, access tokens, private workspace files or unauthorized logs**.

Contribution principles: keep `SKILL.md` small and stable; put detail in `references/`; cite an official source for every new command; do not depend on host-private interfaces in new adapters; and make sure `python scripts/validate_skill.py` passes.

---

<div align="center">

**Make multi-agent collaboration something you can decide on, govern and verify — not an overhead that is on by default.**

*Built for Agent Skills · Powered by the official Kimi Hosted Agents CLI (when authorized)*

</div>
