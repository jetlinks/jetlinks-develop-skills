# 宿主适配与执行收据

只在配置、实现或审查适配器时读取。核心连续性技能可使用 active context；没有已配置且可写的运行态时，不安装后端或建立基础设施来满足本文件。

## 生命周期接口

复用宿主原生能力：压缩前保存/校验，压缩后注入有界主视图，工具前检查确定性前提，工具后保存真实结果。task/thread/issue 的增量 API、已有 event store、FTS 或 memory 可以作为引用后端，但其历史叙述不能替代当前任务契约、源码身份和 Next。

Codex 的映射可以使用 `PreCompact`、`SessionStart(source=compact)`、`PreToolUse`、`PostToolUse`。具体宿主接口见 [OpenAI Codex Hooks](https://learn.chatgpt.com/docs/hooks)。本仓库不安装或注册 hooks，也不保证目标宿主已经传入下列可选上下文；需要在获准的环境另行验证真实触发。

- **PreCompact**：由状态所有者保存一致边界；适配器核对当前源观测，不从 transcript 猜目标或新 Next。
- **SessionStart(compact)**：核对已有状态，只注入主视图、比较结果和允许动作。避免 PostCompact 再重复注入。
- **PreToolUse**：拒绝已失配的源码 mutation、错误动作身份、越权或无有效交付证据的已识别操作。完整重读、额外验证和比较批次属于离线效率观察，不能仅因超预算阻塞工具。
- **PostToolUse**：记录真实结果、事件身份和证据覆盖的源码；启动成功不能当作验证通过。

工具 hooks 不是完整安全边界：未覆盖的工具、shell 变体和未提供的语义字段仍由宿主权限与正常执行规则负责。不要靠猜 shell 文本扩大门禁。

## 可选 Codex 适配器

`scripts/codex_execution_adapter.py` 是独立 CLI。它只在显式配置 state、receipts 或 graph marker 时启用相应能力，workspace 单独存在不启用 hooks：

```text
TASK_CONTINUITY_STATE=<portable-state.json>
TASK_CONTINUITY_RECEIPTS=<execution-receipts.jsonl>
TASK_CONTINUITY_WORKSPACE=<source-workspace>
TASK_CONTINUITY_GRAPH_DIRTY=<optional-index-marker.json>
```

同名 `--state`、`--receipts`、`--workspace`、`--graph-dirty` 参数位于子命令之前。receipts 同目录已有 `continuity.json` 时可复用它，但不会创建 portable state。不要静默修改 `.gitignore`；选择已有非权威运行态位置。

当前实现要求 Python 3 和 **POSIX `fcntl.flock`**（macOS/Linux），依赖 Git 计算内容身份。账本读写通过同一个文件 inode 的共享/排他锁协调；重复事件查重与追加处于同一临界区。不支持该锁的宿主必须使用其等价事务适配，不能静默退回不幂等写入。活跃账本不能被外部进程替换 inode，所有写者都须遵守协议。

### 恢复观测跨 hook 共享

portable state 由状态所有者维护，适配器不覆盖它。已配置 state 时，适配器在同目录保存 `<state>.resume-observation.json`，原子记录当前 snapshot 边界的源码观测。`PreCompact` / `SessionStart` 强制刷新；`PreToolUse` 与 doctor 使用同一边界观测，保证 SessionStart 检出的漂移不能在下一独立 hook 调用中消失。

初次入口或 snapshot 边界变化时建立新观测；同阶段预期编辑沿既有边界继续，不要求每次编辑重建胶囊。已失配状态须由所有者有界对账并保存新 snapshot，不能用后续正确动作抹掉失配。其他适配器的指纹由该宿主的 `observed` 负责，不能将不同算法冒充可比较。

sidecar 仅属于该可选适配器的已配置运行态，不进入源码指纹或交付。已配置但不可写/身份不可读时返回具体诊断，不能假称门禁已生效；普通任务仍可使用核心技能的 active context，不能为消除诊断自动安装持久化设施。

### 源码与任务身份

指纹 v2 使用相对路径、文件类型/执行位和实际内容的统一摘要，覆盖 tracked、untracked、symlink 与嵌套 Git 工作区；已删除文件不参与摘要。单纯 `git add` / `commit` 不改变它。计算会读取参与工作树的实际文件，运行态路径被排除。

算法前缀是 `git-worktree-v2-sha256:`。**旧算法的 snapshot/证据不能直接迁移为有效**：首次升级须重新核对当前源码、保存新 snapshot 并形成适用证据；之后纯暂存/提交复用该证据。指纹不同不意味着必须跑全套，只补覆盖当前验收边界所需的信号。

receipts 按 `task_id`、contract revision、可选 `run_id` 和不暴露本地路径的 workspace identity 精确绑定。已配置 state 的读取或身份校验失败必须拒绝复用，不能降为 workspace-only。仅配置 receipts 的宿主没有任务级身份，应为独立任务配置独立账本；旧未绑定账本不能作为当前验收。

### 事件与异步验证

宿主提供稳定 `event_id`，缺失时使用 tool-use id。相同 kind、event ID 和完整 binding 的重复投递复用原收据；没有稳定事件 ID 时无法承诺跨投递去重。原始日志留在宿主，收据保留有界定位信息。

PostToolUse 处理已识别的源码写入、验证、Agent dispatch/result、commit/push/PR 写操作。验证只有明确退出码 `0` 才记 pass；只有工具级 `is_error=false` 时仍为 unknown。

异步 `exec_command` 返回 `session_id` 而没有退出码时记 pending。后续 `write_stdin` 的输入 session ID、事件 binding 必须命中同一待完成验证；终结收据引用原 start receipt、命令和启动源码。启动/结束源码不一致不能产生当前源码通过证据；无关 session、跨任务 poll 和仍无退出码的 poll 不会将 pending 升为 pass。宿主若不提供这些关联字段，使用明确 locator 的人工证据记录流程，不猜关联。

### Gate 与 CLI

| 动作 | 前提 |
| --- | --- |
| 已识别 `apply_patch / Edit / Write` | 配置 state 时，当前边界的连续性状态支持 READY |
| `git commit` | 当前任务、当前源码有有效 stage checkpoint 和 passed evidence |
| `git push` / 已识别 `gh pr` 写操作 | 当前 checkpoint、委派结果接受状态和 whole-task acceptance evidence 均有效 |

`record-evidence` 记录 review/inspection/artifact/runtime 的 locator、结果和当前身份；它不替代真实验收。阶段集中验证后用 `checkpoint-stage` 引用证据；`accept-assignment` 记录主控接受结果；所有验收完成后 `complete-task`。缺失或失效证据才补充，不按编辑次数生成 checkpoint。`doctor` 检查配置、ledger 错误与 gate，不用“hook 已注册”代替行为验证。

宿主可传入 `continuity_context {recovery_type, identity_match, first_allowed_action_pending, first_allowed_action_id, operation_class, action_id}`，在已匹配恢复中阻止 previous action、已关闭动作回放及错误的第一生产动作。`orchestration_context` 的显式角色、delegation、深度、写集、contract/fork 状态支持对应的前置检查；这些字段的采集和真实 dispatch 覆盖由宿主实现。

代码图按需求更新：源码写入只置可选 graph marker 为 dirty。导航确需该索引时完成增量更新，再调用 `graph-refreshed`；不绑定每次命令或压缩刷新整图。

## 集成验收边界

在实际获准宿主集中验证 hook 触发、运行态位置、匹配恢复、漂移后的下一 mutation、异步验证终结、事件重投与任务切换。脚本单元/CLI 测试不证明安装后的 host wiring。第三方 memory/event-store 只作为可替换后端，安装、hook trust 和网络行为沿用用户已有授权；本技能不要求某个插件。
