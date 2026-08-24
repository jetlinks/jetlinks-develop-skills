# 任务状态、计划压缩与恢复规则

本文件定义环境无关的任务连续性协议。它不要求 Trellis、Git、文件系统、数据库、特定 agent host 或生命周期 hook；宿主扩展可以把这些能力映射进来。

## 1. 生命周期分层

| 制品 | 内容 | 更新方式 | 默认归属 |
| --- | --- | --- | --- |
| 权威来源 | 当前已接受的产品、架构、API、模块与长期约束 | 原位替换过时事实 | 项目已有 canonical docs / contracts |
| 任务契约 | 当前任务目标、范围、非目标、约束和验收信号 | 需求变化时原位修订 | 宿主 task / issue / task state |
| 实时运行态 | 当前阶段、有效假设、最新证据、唯一下一步、阻塞、恢复胶囊 | 稳定边界覆盖写并压缩 | 非权威、临时或 host-managed state |
| 验证证据 | 检查、输入、结果、环境、指纹和时效性 | 按验收矩阵记录 | CI、review、artifact store 或任务证据区 |
| 稳定知识 | 跨任务仍成立的非显然规则 | 更新既有 canonical 来源 | 项目规范、playbook 或 skill |

实时过程不能因“方便恢复”变成权威设计。只有经过确认、长期仍需维护且有明确维护归属的结论才提升；提升时改写当前事实，不复制计划、失败轨迹或最终总结。

提升到权威来源前同时确认：结论已经接受、跨当前任务仍有效、后续维护者需要它、已有 canonical 来源能够原位承载。当前 phase / slice、fixture 或 case 编号、测试通过数、待执行检查、日期进度、阶段提交和完成时间线均属于运行态或验证证据，不能因“已经验证”而提升为产品或架构事实。

## 2. 运行态载体发现

按当前环境实际能力选择，不创建平行体系：

1. 宿主提供的 task、checkpoint、memory、scratchpad、workflow runtime 或 handoff state。
2. 当前项目明确规定的任务运行态，并按其生命周期、权限与版本策略使用。
3. 已存在且确认不会进入权威源码或正常交付的本地临时制品。
4. 没有安全持久载体时，在当前任务上下文维护有界状态；暂停或交接前输出一份可复制的 Recovery Capsule。

不得仅凭目录名猜测是否临时或不受版本控制。不要为运行态静默安装工具、启动服务、修改共享忽略规则、创建数据库，或把状态塞入 README / ADR / API docs。若任务明确要求部署持久化状态能力，再将其作为独立实现和风险决策。

## 3. 当前计划不是流水账

计划只保留：

- 任务契约引用或一句话目标。
- 当前阶段和当前有效工作假设 / 决策。
- 尚未完成的少量阶段及各自验收信号。
- 一个唯一下一动作。
- 一个阻塞区块；没有则写 `none`。

阶段切换时原位替换：移除完成 checkbox、旧操作列表、被否定假设、重复摘要和累计计数。最近完成边界只在 Recovery Capsule 的 `Checkpoint.Validated` 字段保留一个证据指针；审计历史若确实是宿主要求，由宿主的 journal / event log 负责，不能反向膨胀当前计划。

## 4. Recovery Capsule、机器元数据与 Source Snapshot

维护三个有界逻辑视图：

- **Recovery Capsule** 面向模型，回答“目标和约束是什么、当前沿哪条路线、刚验证到哪里、第一动作是什么”。
- **Continuity Metadata** 面向宿主或工具，保存源码摘要、引用 / 规则 revisions、证据 locator、审计指纹和计数；恢复正常匹配时只比较，不把全部内容重新注入模型。
- **Source Snapshot** 回答“语义状态对应哪一份真实源码 / 制品”。

三者可以位于同一物理 artifact，但必须能独立更新和读取。不能用任务摘要替代源码身份，不能用文件摘要推断当前路线，也不能让机器账本挤占模型恢复后的注意力。

### 模型主视图

Recovery Capsule 只保留四个区块：

| 区块 | 必需内容 |
| --- | --- |
| `Contract` | task identity / revision、契约 locator、一句话 observable objective、仍生效的不变量 / 约束、当前 acceptance signals |
| `Checkpoint` | 当前 phase、最近一个 validated boundary 及 evidence pointer、当前 in-flight slice 的稳定 `slice_id` / owner / status / expected changed items |
| `DecisionState` | active hypothesis / chosen decision、最新能区分路线的观察、只保留足以阻止重试的 falsified route；对容易被恢复过程重开的动作保留有界 `do_not_reopen(action_id, reason, reopen_when)`；仍需持续 resurfacing 的关键约束；系统性求解存在 active observation 时再保存其紧凑状态 |
| `Resume` | recovery type、continuity gate、少量精确 anchors、一个带稳定 `action_id` 的执行级 `Next` / `first_allowed_action`、observable signal、blocker 或 residual risk |

默认只向模型注入这个主视图。它必须一次完整可读，不复制任务全文、整张关系图、长 diff、日志、命令流水、所有已完成阶段、引用正文或全部规则。anchors 默认保持少量且足够定位；`3–7` 是常用预算，不是不能调整的固定常数。

### 机器元数据

Continuity Metadata 保存：

- `source_fingerprint`、strength、missing layers 与 expected changed items。
- `ReferencedSources` 的 locator、revision / cursor、extracted facts 与重读条件。
- `LoadedRules` 的 locator、revision / digest、extracted obligations 与重读条件。
- 多 Agent 路线存在时的 `OrchestrationProgram` revision / current stage、冻结的 shared-contract revisions、当前 `RouteDecision` revision、assignment state 与 Result Packet locator。
- 验证证据的 locator、输入 / 环境 identity、适用 acceptance 和 freshness。
- `audit_fingerprint`、`consecutive_matching_audits`、`last_new_evidence`、`previous_productive_action_id`、`pre_compaction_next_action_id`，以及与该 Next 同时捕获的 `instruction_revision_at_snapshot`。

宿主无法提供独立机器存储时，可以把 metadata 放在 capsule 后面的折叠区或同一有界 artifact 中；恢复时仍先读主视图，只在 identity / revision 失配或 `Next` 需要时读取相关 metadata 项。

Source Snapshot 至少记录：source / workspace identity、复合 `source_fingerprint`、指纹强度与缺失层、expected changed items、计算该快照的边界或 locator。`source_fingerprint` 使用环境能提供的稳定身份，例如 VCS revision / tree、change-set ID、构建快照、内容摘要、artifact digest 或任务 revision。不能强制某一种实现。若工作区存在未提交或未版本化内容，指纹必须尽可能覆盖内容而不只覆盖名称或数量：

- 已版本化基线或等价 source revision。
- tracked / managed changes 的内容摘要。
- untracked / unmanaged items 的相对 locator、类型与内容摘要所形成的 manifest 摘要。
- nested workspace、submodule、generated source 或外部挂载中实际参与任务的状态摘要。
- 胶囊声明的 expected changed items，用来区分本任务变化与外部漂移。

适配器对复合指纹做机器交换时，优先使用下列稳定逻辑层；字段名可映射，不能因某宿主没有 Git 术语而降级通用协议：

```yaml
source_fingerprint:
  algorithm: <name + schema version>
  workspace_identity: <stable workspace / source identity>
  base_revision: <VCS / artifact / source baseline>
  managed_change_digest: <tracked / managed content digest>
  unmanaged_manifest_digest: <untracked / unmanaged locator + type + content digest>
  nested_source_digest: <participating nested / generated / mounted source digest>
  expected_changed_items: [<task-owned locators>]
  strength: strong | partial
  missing_layers: [<unavailable logical layers>]
```

算法名和 schema version 是指纹契约的一部分；不同算法的摘要不能直接声称匹配。适配器可以把 `managed_change_digest` 映射成 tracked patch digest，把 `unmanaged_manifest_digest` 映射成 untracked manifest digest，但不得只比较 dirty count、路径数量或 HEAD。`expected_changed_items` 是任务语义范围，不得由当前脏文件清单反推。

某层不可获得时标记 `partial` 和缺失项，不能笼统声称“指纹匹配”。干净且不可变的 version / artifact identity 可以单独构成强指纹；固定 base revision 加 dirty item 数量不能。

### 外部引用账本

只为当前路线实际依赖的外部来源维护有界账本：

```yaml
ReferencedSources:
  - locator: <task / thread / issue / research resource>
    revision: <revision / cursor / updated-at / digest>
    extracted_facts: [<only facts required by DecisionState or Next>]
    reread_when: <revision changed / fact conflicts / missing decision detail>
```

恢复时先用最轻量能力比较 revision / cursor。对 thread / task 类来源优先使用非阻塞 wait / delta（例如 `timeout=0` 和保存的 `afterCursor`），cursor 未变化时禁止再次调用完整 read；cursor 前进时只读取最新增量。只有增量无法解释已记录冲突或缺少唯一决策事实时才扩大到历史页面。未变化且 `extracted_facts` 足够支撑 `Next` 时直接复用；账本不保存整份外部正文或无关历史。

### 技能加载账本与执行级 Next

为当前路线确实依赖的 skill / rule 维护 `LoadedRules`：

```yaml
LoadedRules:
  - locator: <skill or rule resource>
    revision: <version / digest / updated-at>
    extracted_obligations: [<only obligations required by DecisionState or Next>]
    reread_when: <revision changed / route now needs another section / host explicitly requires it>
```

宿主明确要求本轮完整读取某个 skill body 时必须遵守；该要求不等于重新读取它的全部 references、所有协作 skills、research basis 或项目材料。revision 未变化且已提取义务足够时，复用账本；只加载宿主强制正文、当前 `Next` 新需要的规则，或能解释已记录失配的最小片段。

`Next` 与 `first_allowed_action` 必须可直接执行，并且只能属于以下一种：

1. **生产修改**：指出 owner / file / symbol / resource、限定 expected changed items，并写出完成信号。
2. **区分检查**：指出精确工具动作或读取范围、它区分的候选，以及不同结果如何改变决策。
3. **真实阻塞**：指出缺失的权限、用户决定或外部状态，以及解除阻塞所需信号。

系统性求解已经声明 active observation 时，`DecisionState.active_observation` 使用宿主无关的紧凑结构：

```yaml
active_observation:
  id: <同一 hypothesis / boundary / discriminator 的稳定身份>
  revision: <观察契约或装置变化后的 revision>
  decision: <要决定什么>
  boundary: <真实观察边界>
  preconditions: [<必要前提>]
  prediction: <可证伪预测>
  discriminator: <区分规则>
  invalidators: [<无效条件>]
  result: PLANNED | DISCRIMINATING | INVALID | INCONCLUSIVE
  repair_cycles: <同一观察契约已使用的装置修正周期>
  actual_signal: <非 PLANNED 时的稳定摘要>
  evidence_locator: <非 PLANNED 时的证据指针>
```

这不是新的 Capsule 区块，也不为根因明确的简单任务强制启用。细长输入、日志和完整假设表仍留在 evidence locator 后。active observation 存在时，mutation action 额外声明 `purpose`：`solution`、`observation_setup` 或 `observation_repair`；check 和 blocker 不需要伪装成 mutation。

“继续实现某阶段”“继续分析”“熟悉代码”“再看看相关材料”不包含边界和可观察信号，不能从 `RESUME_AUDIT` 进入 `READY`。先在 `SNAPSHOT_REQUIRED` 中把它改写为执行级动作。

准备压缩或暂停时，为 continuation 固化一条最小动作链：

```yaml
Checkpoint:
  in_flight:
    slice_id: <stable slice identity>
    status: planned | active | validation_pending | validation_passed
    owner: <single current owner>
    expected_changed_items: [<bounded locators>]
DecisionState:
  do_not_reopen:
    - action_id: <closed or redundant action identity>
      reason: <evidence-backed reason>
      reopen_when: <specific invalidation condition>
ContinuityMetadata:
  instruction_revision_at_snapshot: <latest user-instruction revision or digest>
  previous_productive_action_id: <stable id or null when none exists>
  pre_compaction_next_action_id: <Resume.Next.action_id>
Resume:
  recovery_type: COMPACT_CONTINUATION | COLD_HANDOFF | EXTERNAL_RETRY
  first_allowed_action:
    action_id: <same id as pre_compaction_next_action_id>
```

`previous_productive_action_id` 只回答“刚才真正做了什么”，不能被恢复器当成默认续跑动作；它与 `pre_compaction_next_action_id` 不同时，压缩后的第一项生产动作若又命中 previous 即为上一动作回放。`do_not_reopen` 只保存有现实重放风险且有明确失效条件的少量动作，不能演变成历史清单。若用户在压缩后给出新指令，先比较独立的 instruction revision；确有变化时最新指令优先并刷新契约 / Next，不能把合法改线误报成恢复偏航。

### 多 Agent 程序运行态

当编排能力建立阶段化程序时，只保存恢复和集成需要的控制面，不保存子 Agent 的过程日志或完整上下文：

```yaml
OrchestrationState:
  program_id: <stable id>
  program_revision: <revision>
  current_stage: <stage id>
  shared_contract_revisions: {<contract id>: <frozen revision>}
  route_revision: <current RouteDecision revision>
  assignments:
    - assignment_id: <stable id>
      status: routed | active | collected | accepted | rejected | blocked | stale
      source_fingerprint: <assigned source identity>
      dispatch_receipt: <opaque host receipt when dispatched>
      result_locator: <terminal Result Packet locator when available>
      write_set: [<exclusive task-owned locators>]
  integration_owner: <primary owner>
  critical_path_next: <wait, accept, integrate, dispatch next stage, or blocker>
```

恢复时先用宿主最轻量的 agent-status / wait / result-delta 能力对账这些身份。`active` assignment 继续等待或 steer，`collected` assignment 进入接受检查，已有 terminal locator 的 assignment 不重新读取完整子线程；只有 program、stage、shared contract、source identity 或 result 发生失配时才扩大。不得因上下文压缩重建相同分工、重复 dispatch，或让新 Agent 接管仍有活跃 owner 的 write set。阶段完成后覆盖 `current_stage` 与 assignment 集合，只保留最近 accepted boundary 的 evidence locator，不把每轮调度历史累积进主视图。

### 跨压缩恢复指纹

Continuity Metadata 中的 `audit_fingerprint` 对当前 task / contract revision、Source Snapshot、ReferencedSources revisions、`DecisionState`、Anchors 和执行级 `Next` 做稳定摘要；不要把状态名、审计计数或时间戳纳入摘要。它用于识别“仍是同一个恢复切片”，不是替代各组成事实。

- 每次恢复审计与上次 `audit_fingerprint` 匹配，且其间没有生产修改、产生区分结果的检查、相关新证据或真实阻塞报告时，递增 `consecutive_matching_audits`。
- 相关 source / reference / contract、`DecisionState`、Anchors 或 `Next` 因新事实改变时，刷新指纹并把计数重置为 `1`；仅发生上下文压缩、重新表述或重复读取不能清零。
- `last_new_evidence` 只记录最近改变决策或验收状态的 locator；没有则写 `none`。普通恢复核对不冒充新证据。
- `first_allowed_action` 必须是 `Next` 的可执行实例；它可以是一次有界 mutation、discriminating check 或 blocker report，不能是再次恢复审计或材料重读。
- `pre_compaction_next_action_id` 必须与 `Next.action_id`、`first_allowed_action.action_id` 相同；`post_compaction_first_productive_action_id` 由轨迹在恢复后观测，匹配的 compact continuation 中也必须相同。仅仅重新表述胶囊不能改变这些 identity。

主视图只保存路线索引；引用 / 规则账本与证据细节进入机器元数据。即使物理上共用一个文件，恢复正常匹配时也不能把整个 metadata 区重新注入模型。

## 5. 连续性状态门禁与刷新边界

状态含义：

| 状态 | 含义 | 允许动作 |
| --- | --- | --- |
| `READY` | Contract、Checkpoint、DecisionState、Source Snapshot 和执行级 Resume 对应同一当前事实；机器元数据 revisions 已匹配 | 执行 `first_allowed_action` 定义的有界实现、区分检查或阻塞报告 |
| `SNAPSHOT_REQUIRED` | 新事实已经使胶囊或 Source Snapshot 不足以安全决定下一生产动作 | 只做有界只读对账、计算指纹和覆盖写运行态；禁止继续生产修改 |
| `RESUME_AUDIT` | 刚发生压缩、恢复、暂停后继续或交接，尚未证明保存状态仍对应当前事实 | 按恢复预算核验身份、引用、`DecisionState`、Anchors 与 `Next`；匹配后转 `READY`，失配则转 `SNAPSHOT_REQUIRED` |

以下任一事件发生时立即进入 `SNAPSHOT_REQUIRED`，不能等到下一个“成功阶段”再补：

- 新证据改变 active hypothesis、失败签名、解法层级、验收通过 / 失败状态或唯一 `Next`。
- 观察从 `PLANNED` 变成完成态、实际信号命中 invalidator、观察 revision / result 改变，或结果要求重设 boundary / discriminator。
- 用户、外部引用或权威契约的新 revision 改变当前路线依赖的事实。
- source identity 出现未声明的 changed item、nested source 漂移或预期切片之外的内容变化。
- 一个声明的 in-flight 实现切片完成、被放弃或需要换成另一切片。

同一 `READY` 状态可以授权一个预先声明、范围有界的 in-flight 实现切片；切片内 expected changed items 的连续编辑不要求每条命令刷新。若编辑暴露新根因、改变验收语义、越出 expected items 或决定改走另一条路线，则例外地立即进入 `SNAPSHOT_REQUIRED`。这使门禁约束语义变化，而不是制造新的逐操作流水账。

`SNAPSHOT_REQUIRED` 期间允许读取直接失配项、计算复合指纹、更新 Attempt / evidence、压缩计划和覆盖写胶囊；不允许继续修改生产代码、生产配置、对外契约、持久状态，或继续调整将决定解法方向的观察装置。刷新完成并确认 `Next` 唯一后才能回到 `READY`。

指纹为 `partial` 时可以继续只读诊断。生产修改前必须做到二选一：补齐与当前任务相关的缺失层；或明确记录无法核验的层、残余身份风险、expected changed items 和严格限定的修改范围。后者是带风险的 `READY`，不是“完整匹配”。

只在以下语义边界覆盖刷新，不在每个命令后追加：

- 用户确认或改变任务契约。
- 根因模型、解法层级或主路线变化。
- 一个连贯阶段完成并获得验收证据，或验证失败改变了失败签名、验收状态或下一步。
- 准备暂停、交接、主动压缩或预计上下文即将丢失。
- 外部变化使任务身份、source fingerprint 或锚点失效。

刷新时覆盖旧状态，并使 Recovery Capsule、Continuity Metadata 与 Source Snapshot 指向同一边界。尚未验证的工作只能进入 `Checkpoint.In-flight`，不能写成 `Checkpoint.Validated`。若宿主有阶段 commit、build、snapshot 或 review ID，可作为证据 locator；通用协议不要求其中任何一种。

## 6. 恢复类型、算法与读取预算

先按触发原因区分三种恢复，不能把所有暂停都升级成完整接管审计：

| 类型 | 适用触发 | 默认预算 | 必须结果 |
| --- | --- | --- | --- |
| `COMPACT_CONTINUATION` | 同一任务 / 会话刚发生自动或手动上下文压缩 | 读取最新指令与胶囊；最多一个并行工具批次比较 source、contract、reference cursor 和 rules revision | 匹配时在恢复当轮执行 `first_allowed_action`；失配时只对账失配项 |
| `COLD_HANDOFF` | 新 owner 首次接管、没有可信胶囊，或任务 / source identity 无法关联 | 一次有界 takeover audit，可读取任务契约、最近有效 checkpoint、source identity 和建立精确 anchors 所需的最小范围 | 建立新的有界状态和执行级 `Next`，或报告一个真实阻塞 |
| `EXTERNAL_RETRY` | 503、超时、连接中断、审批等待后重试等外部失败 | 比较外部 operation / request identity 与相关 revision；源码和契约未变时不审计 workspace | 查询幂等状态或重试同一 `Next`；只有外部结果改变任务事实时刷新快照 |

`EXTERNAL_RETRY` 若无法判断上一次有副作用操作是否成功，先用 operation id、幂等键、远端状态或等价只读能力消除不确定性，不能盲目重复；这仍是外部结果核验，不是完整上下文恢复。

恢复快速路径先于普通任务分类与 focused-skill 路由：

```text
最新指令 + Recovery Capsule 主视图
  -> 轻量比较 Source Snapshot、contract / reference / rule revisions
  -> 全部匹配且 Next 可执行：RESUME_AUDIT -> READY -> first_allowed_action
  -> 任一失配或 Next 不可执行：SNAPSHOT_REQUIRED -> 只对账失配项
```

匹配恢复默认不加载 `$systematic-solving`、`$code-navigation`、交付 skill、完整 PRD / research / task history 或仓库概览。只有新失败或假设变化需要重建问题模型，anchor / owner / impact 失效需要重新导航，阶段 checkpoint 或最终交付需要交付 skill。技能可用不构成加载理由。

1. `COMPACT_CONTINUATION` 与已有可信状态的 resume 先进入 `RESUME_AUDIT`；分别比较用户最新 instruction revision 与 `instruction_revision_at_snapshot`，再读取任务契约和 Recovery Capsule 主视图，确认任务身份、目标、关键约束、in-flight `slice_id` 和执行级唯一下一步。instruction revision 变化时进入 `SNAPSHOT_REQUIRED`，按最新指令刷新路线；未变化时不得用旧症状或恢复叙述覆盖已保存的 Next。`COLD_HANDOFF` 先建立这些状态，`EXTERNAL_RETRY` 则保留原 gate 和 `Next`。
2. 使用当前环境最轻量的只读能力比较 Source Snapshot、预期 changed items，以及机器元数据中的引用 / 规则 revisions；匹配时不读取完整 metadata、原始证据或外部正文。
3. 计算当前 `audit_fingerprint`，核对 Contract、Checkpoint、DecisionState、少量 Anchors 和 `Next` 是否彼此一致；不要仅因 source fingerprint 匹配就跳过语义核验。
4. 指纹、引用和语义状态均匹配时递增或初始化 `consecutive_matching_audits`，显式执行 `RESUME_AUDIT -> READY`，只加载宿主要求的当前 skill body 和 `Next` 新需要的规则，然后立即执行 `first_allowed_action`；对 `COMPACT_CONTINUATION`，核验调用必须合并在最多一个可并行工具批次中，且 productive action 必须发生在同一恢复轮。不重读 research basis、已提取外部历史、整个任务树或仓库总览。
5. 引用 revision 变化但 source 匹配时转为 `SNAPSHOT_REQUIRED`，先读取引用增量并更新 `extracted_facts`；不因此重新扫描源码。
6. source 部分失配时转为 `SNAPSHOT_REQUIRED`，先检查失配 changed items 或 artifact，只扩大到解释失配所需的生产者、消费者或所有权边界，并重写三个逻辑视图。
7. 任务身份、契约或 source state 无法建立时停止实施，向用户请求一个聚焦的决定；不要猜路线。

若宿主能将三个逻辑视图和轻量 observation 导出为 JSON，可以调用 `scripts/validate_continuity_state.py` 执行确定性门禁。核心输入字段采用 `recovery_capsule`、`continuity_metadata`、`source_snapshot` 和可选 `observed`；`observed` 只提供当前 source fingerprint、contract revision、引用 / 规则 revisions 与同边界标识，不复制正文。校验器必须检查：

- `Contract / Checkpoint / DecisionState / Resume`、Continuity Metadata 与 Source Snapshot 是否完整并指向同一 `boundary_id`。
- `Next` 与 `first_allowed_action` 是否为 mutation / check / blocker，是否含 owner、bounded scope 和 observable signal，以及两者是否同一稳定 action identity。
- `Checkpoint.Validated` 是否同时有 evidence locator 与真实 checkpoint identity；只通过测试但未 checkpoint 的阶段不能伪装成 validated。
- partial fingerprint 是否列出 missing layers、expected changed items 与 residual identity risk。
- source / contract / referenced sources / loaded rules 的轻量 observation 是否匹配；缺 observation 时保持 `RESUME_AUDIT`，失配或 schema 无效时建议 `SNAPSHOT_REQUIRED`。
- active observation 存在时，其 revision / result 是否与轻量 observed state 匹配，以及 mutation purpose 是否受结果门禁允许：`DISCRIMINATING -> solution`、`PLANNED -> observation_setup`、首次 `INVALID -> observation_repair`；`INCONCLUSIVE` 或已用完修正预算不能直接 mutation。

该脚本只返回 diagnostics、comparisons 和 suggested gate，不写运行态、不修改源码、不阻断工具、不提交或发布。宿主 adapter 负责安全采集 observation、解释 locator，并按授权应用状态转换；不能因为脚本可用就在每条命令后调用。

默认恢复读取预算只包含：最新指令、任务契约、胶囊主视图、复合指纹 / revisions 的比较结果、宿主强制规则和 `Next` 必需的少量 anchors。任何超出预算的读取必须对应一个明确的身份 / 指纹 / 引用 / 锚点失配，并说明它将消除哪项不确定性。恢复后的第一项生产性动作必须直接服务于 `Next`；“继续读取以熟悉项目”不是生产性动作。

宿主有并行工具能力时，`COMPACT_CONTINUATION` 的 source fingerprint、contract revision、reference cursor、LoadedRules revision 比较应作为一个并行批次发出；没有并行能力时仍只允许一个等价的有界比较阶段，不能把四项拆成多轮分析。以下指标作为 continuation trace 的默认硬门禁：

- `resume_audit_tool_rounds <= 1`
- `full_thread_reads == 0`
- `unchanged_reference_reads == 0`
- `recovery_commentary_only_turns == 0`
- `first_productive_action_turn == resume_turn`
- `pre_compaction_next_action_id == post_compaction_first_productive_action_id`
- `recovery_route_deviation_count == 0`
- 第二次及后续 matching audit 的完整 reference / skill / workspace 重读为 `0`

这些门禁只约束状态匹配的 `COMPACT_CONTINUATION`。`COLD_HANDOFF` 和已记录失配的恢复必须报告实际读取成本与原因，但不伪装成快路径失败。

恢复审计通过后的第一项生产性动作必须服务于胶囊的 `Next` 和验收信号。相邻 TODO、旧方案或新可用工具都不能自动扩大范围。连续匹配恢复按以下止空转门禁处理：

在 identity、instruction revision 和引用均匹配的 `COMPACT_CONTINUATION` 中，下列行为在首个正确生产动作之前一旦发生即记为 route deviation，而不是“必要恢复成本”：完整 skill / rule set 重载、workspace / repository-wide scan、未变化外部历史完整重读、命中 `do_not_reopen` 的动作，以及 `previous_productive_action_id != pre_compaction_next_action_id` 时重新执行 previous。后面再执行正确 Next 不能抵消已经发生的偏航。

- 第一次允许在默认预算内完成正常审计，随后必须转 `READY`。
- 默认从第二次且没有 `last_new_evidence` 或生产性动作时，只比较保存的组成事实与当前轻量 identity；禁止完整重读 skills / PRD / research、仓库总览或重建同一系统图，匹配后立即执行 `first_allowed_action`。
- 默认第三次及以后仍只有分析时判定为空转；不能再提出“先恢复 / 再熟悉 / 下一步将实现”。本轮只能执行精确 `Next`、运行一项能区分假设的检查，或明确报告真实阻塞。

第二 / 第三次门槛是可通过真实轨迹调优的操作默认值，不是论文给出的自然常数。宿主可以按风险调整阈值，但必须保持两个不变量：同一恢复切片不能无限重复消费分析轮次；没有新证据时，后续恢复的读取范围不能扩大。

生产性动作是限定范围内的生产修改、实际产生并记录区分结果的检查，或使任务进入可处理等待状态的真实阻塞报告。重复核对相同 revision、复述设计、重建相同系统图、重新加载相同规则、更新计数或声称“准备实施”都不算。只有用户改变目标、相关 source / reference / contract 漂移、新证据改变路线，或生产性动作已经发生，才按新边界刷新 / 重置停滞状态；压缩本身不能清零。

## 7. 验证证据生命周期

交付或阶段切换不自动使证据失效。复用前核对：

- 证据覆盖的源码 / 制品与当前 source fingerprint 相符。
- 相关测试、配置、依赖、工具链、base、输入数据和检查语义未发生会改变结果的变化。
- 运行环境仍等价，检查本身不具有已过期的时间、安全或外部状态属性。
- 证据能映射到当前验收矩阵，而不只是某个曾经成功的命令。

只补跑缺失、失效、失败或有时效性的检查。不能建立有效映射时，如实降级为待验证，不机械全量重跑来掩盖证据边界。

## 8. 条件式版本化交付

先发现当前环境是否提供版本控制、局部 checkpoint、远端共享和 review / change-request 能力：

- 无版本控制：在阶段验收后记录宿主 checkpoint 或证据 fingerprint；不能伪造 commit。
- 有版本控制但无远端 review：每个连贯阶段验证后创建一个本地、可恢复的逻辑 checkpoint；不按文件、命令或小步骤切分。
- 有 VCS 与 review：每个连贯阶段集中验证后创建一个本地 commit / change；整个任务和总体验收完成后才统一 push，并创建或更新一次 task-level PR / review。
- 用户明确要求中间共享时，只更新同一个 draft / review；不能为每个阶段建立新的 PR，也不能用 review 评论记录命令流水。

进入交付阶段前先把已有证据映射到验收矩阵。相关 source fingerprint、测试、配置、依赖、base、环境和检查语义仍有效时直接复用；只补跑缺失、失效、失败或有时效性的检查。提交元数据或工作流阶段变化本身不使证据失效。

具体分支名、受保护分支、commit 格式、push 权限、review 模板和发布门禁由宿主 / 项目扩展定义，通用技能不硬编码 GitHub、GitLab 或某个仓库策略。

在提供版本化 checkpoint 的环境中，阶段进入 `Checkpoint.Validated` 前必须已经创建实际本地 checkpoint，并记录其 identity；只有验证通过但尚未 checkpoint 的阶段仍为 `Checkpoint.In-flight(validation=passed)`。checkpoint 之后若 source tree 与被测内容等价，checkpoint metadata 变化本身不使验证证据失效。

## 9. 可选宿主自动化

若宿主提供 lifecycle hooks、checkpoint callbacks 或 equivalent automation，可选择：

- 在压缩前保存有界 Recovery Capsule、Continuity Metadata 与当前 Source Snapshot；保存失败时显式留下 `SNAPSHOT_REQUIRED`，不能伪装成功。
- 在压缩 / 恢复后将状态置为 `RESUME_AUDIT`，只注入胶囊摘要、source strength、`audit_fingerprint`、instruction revision match、匹配计数、`previous_productive_action_id -> pre_compaction_next_action_id` 动作链、唯一 `Next` 和 locator。
- 在停止时检查是否存在执行级唯一下一步、未映射验收项、未说明的失败，或连续匹配恢复后仍只有分析动作。
- 在工具调用后只采集证据 locator，不把完整输出持续注入上下文。
- 用外部来源 revision / cursor 自动维护增量引用账本，未变化时不再次注入完整历史。
- 在保存前计算宿主可提供的复合 source fingerprint，并对缺失层标记 `partial`。
- 在宿主确实支持且覆盖目标工具时，阻止 `SNAPSHOT_REQUIRED` / 未完成 `RESUME_AUDIT` 状态下的生产修改；hook 不能覆盖的工具仍由语义门禁负责。

这些是可选适配，不是技能依赖。自动化必须有界、可审查、可禁用，不能修改问题结论、替代任务证据或把私有数据发送到未授权位置。注入内容设置严格大小上限；溢出时保存 locator 而不是把长日志或完整胶囊反复塞回上下文。

宿主自动化应保存完整有界状态，但 `SessionStart(source=compact)` 或等价入口只注入模型主视图、source strength、revision match summary、匹配计数和 `first_allowed_action`。原始 evidence、完整账本、长规则和完整系统图保持按 locator 拉取。

第三方 memory / event-index / compaction 插件可以承担事件持久化、全文 / 语义检索和 lifecycle wiring；不得让插件生成的历史叙述取代 Capsule、Source Snapshot 或 gate。优先复用成熟后端，不复制数据库、FTS、embedding、transcript archive 或 hook installer。安装前核对宿主版本、许可证、数据位置、网络行为、依赖、hook trust 和注入上限；安装是显式的环境变更，不因技能可用而自动发生。具体选择规则见 [`host-adapters.md`](host-adapters.md)。

## 10. 标准化轨迹与评测适配

宿主可把真实执行记录转换成 `scripts/evaluate_continuity_trace.py` 接受的有序 `events`。标准事件至少包含 `type`，按事件种类补充：

- 读取：`target`、`revision/source_fingerprint`、`scope`、可选 `recovery_id`。
- 恢复：顶层或事件记录 `recovery_type`、`resume_turn`、`identity_match`、`matching_audit_number`；恢复核验读取再记录 `continuity_phase=RESUME_AUDIT` 和同一并行批次共享的 `tool_round`。
- 外部引用：读取事件标记 `target_kind=thread|task|issue|reference|research`、`cursor_changed/revision_changed` 与 scope；cursor 未变时不得生成 read 事件，若实际发生则评测为 `unchanged_reference_reads`。
- 恢复 commentary：只有状态复述且没有生产动作的轮次记录 `commentary` / `recovery_commentary`，用来检测“本轮只恢复、下轮再执行”。
- 生产动作：`action_id`、`turn`、`productive`、`serves_next`、可选 `recovery_id`。continuation 顶层同时记录 `previous_productive_action_id`、`pre_compaction_next_action_id`、压缩前后 instruction revisions；评测器输出 `post_compaction_first_productive_action_id` 和 action identity continuity。
- 恢复入口动作：adapter 可用 `recovery_action_class=full_rule_reload|workspace_rescan|full_history_reread|suppressed_action_replay|previous_action_replay` 标准化；核心评测器也会从通用 event type / scope 推断可确定的类别。只有匹配的 compact continuation 在首个生产动作前把这些类别计为偏航。
- 验证：`check_id`、source fingerprint、input revision、environment；等价四元组用于发现无依据重复执行。
- 权威 artifact 写入：`content_classes`，由 adapter 标记 progress、test counts、todo、attempt history 等运行态类别。
- 代码图注入：decision question、task anchor、task / graph source fingerprint、目标 / 图语言与范围。
- 约束与证据消费：稳定 `constraint_ids` / `evidence_ids`，用于 full-context / capsule / ablation 检测真正有害的上下文丢失。
- 观察声明 / 结果：`observation_id`、`observation_revision`、boundary / discriminator 的宿主映射、`result` 和 `changes_decision_state`；同一 hypothesis / boundary / discriminator 即使换工具也保持同一 id。
- 观察装置修正：每个语义修正批次记录一个 `observation_apparatus_changed`，不按文件或命令拆分；更换 hypothesis、boundary 或 discriminator 后使用新的 observation id。
- 解法变化：mutation / action 标记 `purpose=solution` 并引用授权它的 observation id / revision；观察 setup / repair 使用对应 purpose。若复杂路径要求区分证据，轨迹或事件标记 `requires_discriminating_evidence=true`。
- 状态刷新：改变 DecisionState 的观察后记录 `snapshot_refreshed`；评测器据此识别陈旧胶囊下的解法变化。

标准化时保留真实发生顺序和来源，不能把事后总结伪造成当时已注入的约束或证据。核心评测器不读取 agent 私有思维，不判定业务代码正确性，也不绑定具体 trace API；adapter 仅做可审计的字段映射。评测在一个阶段或一组 continuation 轨迹完成后集中运行，不在每次工具调用后制造新的验证循环。
