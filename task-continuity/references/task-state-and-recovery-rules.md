# 任务状态与恢复协议

只在实现结构化状态、冷交接或处理复杂失配时读取相关段落。普通保存与匹配恢复遵循技能入口即可；不需要预先加载整份协议。宿主、文件系统、Git、hooks 和多 Agent 都是可选能力。

- [生命周期与载体](#生命周期与载体)
- [模型主视图与机器状态](#模型主视图与机器状态)
- [多轮指令与主线](#多轮指令与主线)
- [恢复判定](#恢复判定)
- [可选复杂状态](#可选复杂状态)
- [证据与交付](#证据与交付)
- [结构化工具与效率诊断](#结构化工具与效率诊断)

## 生命周期与载体

任务契约保存当前已接受的目标与约束；运行态保存当前阶段、最新有效事实、下一步和阻塞；证据保存检查结果及适用身份。它们不因需要恢复而成为产品或架构事实。

优先复用宿主 task、checkpoint、memory、scratchpad 或项目既有临时状态。没有安全持久位置时，使用 active context，并在交接前给出有界胶囊。不要为此安装工具、修改共享忽略规则、创建数据库，或把计划写进 README / ADR / API 文档。只有用户实际要求持久化能力时才开展相应实现。

当前计划是状态投影：目标、当前阶段、剩余验收工作、一个 Next、阻塞。完成边界保留证据指针；审计历史留在已有事件或日志后端。跨任务仍成立的知识才适合原位更新其权威来源，沿用已有授权和维护责任。

## 模型主视图与机器状态

模型主视图使用四个区块：

| 区块 | 需要保留的信息 |
| --- | --- |
| `Contract` | task identity、当前 semantic revision、原目标、约束与验收、权威契约 locator |
| `Checkpoint` | 当前 phase、in-flight slice 的身份/owner/范围、最近有效边界与 evidence/checkpoint 指针 |
| `DecisionState` | 当前决定或假设、最近改变路线的观察、关键未决问题、有重放风险的已关闭动作 |
| `Resume` | recovery type、gate、精确 anchors、唯一 Next / first_allowed_action、临时插入的返回点 |

这些信息必须完整表达当前决定。不要把目标、约束、action ID、路径或条件机械截断；超过建议大小时给诊断并由保存者压缩无关历史，不能为达到长度目标删除仍有效的用户要求。通常少量 anchors 足够，`3–7` 只是观察目标。

机器元数据保留必要的 source digest、引用/规则 revisions、证据输入/环境/时效、conversation cursor、directive revision、审计计数，以及动作链。Source Snapshot 单独表明语义状态对应哪份源码或制品、预期变化范围、指纹强度与缺失层。三者可共用一个物理 artifact；正常恢复只注入主视图和比较结果。

可选 JSON 交换结构：

```text
recovery_capsule:
  contract: boundary_id, task_id, revision, locator, objective, constraints[], acceptance[]
            optional accepted_constraints[{id, text, scope?}]
  checkpoint: boundary_id, phase, validated[{stage, evidence:{locator}, checkpoint:{id}}]
              in_flight:{slice_id, status, owner, expected_changed_items[]}
  decision_state: boundary_id, active_hypothesis, acceptance_status
                  optional do_not_reopen[{action_id, reason, reopen_when}]
  resume: boundary_id, recovery_type, gate, anchors[], next, first_allowed_action
continuity_metadata:
  boundary_id, audit_fingerprint, consecutive_matching_audits
  directive_revision_at_snapshot, conversation_cursor_at_snapshot
  pre_compaction_next_action_id, previous_productive_action_id
  referenced_sources[{id, revision}], loaded_rules[{id, revision}]
source_snapshot:
  boundary_id, source_id, source_fingerprint, strength, locator
  expected_changed_items[], missing_layers[]
observed:
  boundary_id, source_fingerprint, contract_revision, directive_revision
  conversation_cursor, referenced_sources:{id:revision}, loaded_rules:{id:revision}
  optional message_class, message_effect
```

同一快照的 `boundary_id` 必须一致。字段细节以 `scripts/validate_continuity_state.py` 为执行定义；别为普通任务补齐这份宿主 schema。`instruction_revision_at_snapshot` / `observed.instruction_revision` 是 directive 的旧字段别名；不要将 cursor、directive 和 contract 合为一个计数器。

Next 是一个执行级动作：稳定 `action_id`，`type=mutation|check|blocker`，明确 `owner`、`scope` 和 `observable_signal`。`next` 与 `first_allowed_action` 指向同一动作；压缩前保存的 `pre_compaction_next_action_id` 必须相同。`previous_productive_action_id` 用于识别已完成工作的重放，不能作为缺失 Next 的替代项。

`Contract.constraints` 保存原有有效约束。需要跨轮增量时，`accepted_constraints` 使用稳定 id；同一 id 的已接受修订替代旧文本，不复制提醒；`status=revoked` 显式撤销该 id，投影移除旧正文。旧字符串约束没有 id 时，由保存者原位修订其列表，不能靠猜测撤销。保存新边界时累计保留未撤销记录，不能只保留最近一条用户消息。投影把这些记录与原 constraints 合并，同时保留原 objective、完整作用范围和当前指令身份。

### Source Snapshot 与引用

指纹使用当前环境能提供的最强身份；有未提交或未版本化内容时覆盖实际内容、文件类型、相关嵌套源码与预期变化范围，不能只比较 HEAD、dirty count 或路径数量。记录算法及版本；不同算法不能宣称匹配。某个任务相关层无法获得时标为 `partial`，列出缺失层、残余风险和具体作用范围，有界诊断可继续，不能假称完整身份已匹配。

规范化 partial 状态保留 `missing_layers` 与 `residual_identity_risk`；相同 partial 指纹只证明已覆盖层相同。当前 Next 的修改或验收依赖缺失层、或无法确定缺失范围时，进入 `RESUME_AUDIT`，先有界观察，不能投影为可执行 mutation。`type=check` 且 `purpose=observation_setup | observation_repair` 可补齐恢复观察；该检查本身不证明验收。

只有需要证明缺失与当前动作无关时，条件提供 `source_snapshot.missing_layer_scopes`：以每条 missing layer 为键、工作区内路径列表为值，必须覆盖全部声明。Next 的既有 `scope` 应包括执行和验收所需源路径。`source_snapshot.locator` 只有在当前可核验为本地绝对目录时才作为物理根；参与准入的路径严格解析到实际对象，且必须仍在该物理根内。同一文件对象或祖先 / 后代边界视为相交；不同文件对象才足以在无目录展开时证明明确文件 scope 无关。目录边界本身不证明未知子项没有别名，未获得宿主核验的规范化边界闭包时保持 unknown，不扫描整个工作区。远端 / 虚拟根、无法解析、通配符、物理越界或范围不完整均不能靠词法不交放行。可证明不相交时允许当前有界动作，但投影仍保留 partial 身份和残余风险，不宣称全局身份完整。普通 strong 状态无需该字段。


只为当前路线依赖的外部资源保存 locator、revision/cursor、提取事实和重读条件。已有事实足够且 revision 未变时复用；cursor-capable task/thread 先用轻量 wait/delta，只有增量无法解释冲突才回读必要历史。`LoadedRules` 同样保存 revision 与已提取义务；技能可用或发生压缩本身不是重读理由。

## 多轮指令与主线

新消息默认补充当前工作。先看语义影响，再调整状态；用户明确的修改优先于快照。

| 消息 | 状态处理 |
| --- | --- |
| `QUERY` | 回答状态或疑问，保留目标、约束和 Next，继续工作 |
| `REMINDER` | 按稳定约束身份去重，不创建新任务或重派所有 Agent |
| `NEW_CONSTRAINT` | 保存新增/修订约束正文与范围，更新 directive；只使受影响的动作/Assignment 失效 |
| `CONTRACT_CHANGE` / `OVERRIDE` | 用户确实改变或替换目标/契约，刷新 contract 并使依赖旧 revision 的工作失效 |
| `TEMPORARY_INTERRUPT` | 保存返回锚点，处理插入目标，满足返回条件后恢复原主线 |
| `OBSERVATION` / `DECISION` | 只有实际改变决定、验收或 Next 的新事实才刷新相关状态 |

cursor 前进时 JSON `observed.message_effect` 至少包含 `affects_saved_next` 与 `affected_assignment_ids`。`NEW_CONSTRAINT` 还需 `accepted_constraints[{id,text,scope?}]`，避免只有 revision 变化却丢失真实要求。局部约束不影响 Next 时允许保留该动作，并在投影中带上新约束；保存下一边界时把增量并入 Contract。

material interrupt 的 `mainline_return_anchor` 保存 `interruption_id`、`original_task_id`、`saved_stage`、`saved_next_action_id`、`frozen_contract_revision`、`active_assignment_ids`、`source_fingerprint`、`interrupt_objective`、`resume_condition`。ACTIVE 时不能执行原主线 Next；`RESUME_READY` 时核对任务、契约、源码和动作身份，失配先对账。用户已明确替换主线时，不再执行旧返回动作。

## 恢复判定

- `COMPACT_CONTINUATION`：使用既有状态，比较身份和最新消息影响，匹配后执行保存动作。
- `COLD_HANDOFF`：身份或落点缺失时，先进行有界接管对账。
- `EXTERNAL_RETRY`：任务和身份未变时，仅核对原外部 operation 的结果和幂等状态。

`READY` 只由动作身份和必要前提支持；缺观测保持 `RESUME_AUDIT`，真实失配转为 `SNAPSHOT_REQUIRED`。失配范围可能是源码、契约、引用、已接受约束、证据或 Next；只读变化范围，更新状态后再做依赖该状态的 mutation。可以继续独立且已授权的工作。不能建立身份或需要实际用户决定时报告具体阻塞，不为例行恢复重新请求授权。

匹配恢复默认只读主视图、轻量比较结果和 Next 必需锚点；可并行的比较合并执行。宿主强制读取、合法串行依赖或新事实可能增加轮数，应解释其用途而非制造事件满足指标。实际执行必须继续服务于有效 Next 和验收；完成旧动作、相邻 TODO、无关工具可用性不能改变主线。

## 可选复杂状态

简单任务不需要以下结构；它们存在时恢复必须忠实保留，不能重建一个更方便的契约。

- **观察**：`active_observation` 保存 id/revision、假设边界、prediction/discriminator、actual signal、result、证据 locator 与前提/失效条件。`DISCRIMINATING` 可支持所关联的解法变化；`PLANNED`、`INVALID`、`INCONCLUSIVE`、`SCOPE_INVALID` 只能支持相应的有界观察准备、修复、对账或真实阻塞，不能冒充解法证据。
- **语义分叉**：`semantic_fork` 保留 decision question、完整 options 与架构影响、`OPEN|RESOLVED`、证据能否决定以及 resolution 的来源/决定/locator。OPEN 不能授权依赖未决契约的实施或 review；沿保存的区分检查或决策阻塞继续。
- **已停止的调查**：已有 `evidence_budget` / `evidence_reopen` 表示明确的调查状态与重开理由，不是因读取次数自动产生的新权限。STOPPED 的任务先保留其决定/阻塞；有效新事实或用户决定可重开，记录相关 revision、原因和原 round。计数本身不证明失败。
- **委派**：保留 program/route/共享契约 revision、活跃 Assignment 身份与状态、结果 locator 和集成 owner；核对现有状态后再 dispatch/wait/integrate，不重派仍活跃或已经记录结果的任务。角色和权限规则由编排能力维护。

## 证据与交付

证据复用需覆盖当前源码/制品、任务契约、输入与检查语义、环境、有效期和当前验收项。异步工具成功启动不是验证通过；最终结果必须关联启动身份。无有效证据时如实标记待验证，不用叙述替代结果。

在连贯阶段结束后集中验证，补充缺失、失败、失效或时间敏感的信号。提交、暂存和 review 本身不使内容证据失效。版本化环境沿用用户和项目授权的 checkpoint / 提交 / 共享方式；本技能不自动 commit、push 或创建 review，也不重复请求已有授权。

## 结构化工具与效率诊断

- `validate_continuity_state.py` 检查同边界状态、动作与身份、消息影响、可选观察/分叉前提，输出 gate 和诊断。
- `prepare_resume_context.py` 投影主视图及比较结果。保留全部有效约束与精确动作，失配时不提供可执行的 first_allowed_action。大小超出目标给出 `projection_warnings`，不能静默截断语义或因此拒绝正确动作。
- `evaluate_continuity_trace.py` 使用真实宿主有序事件评估已观察到的不变量和效率，不判定业务成果本身。
- `codex_execution_adapter.py` 的配置、边界观测、收据和平台限制见 [host-adapters.md](host-adapters.md)。

评测要分开报告：

1. 实际验收结果，目标与约束是否保留，task/source/contract/action 是否准确，权限与证据是否有效。
2. 恢复读取量、工具批次、首次有效动作轮数、重复读取/验证、额外 commentary 与审计计数。

一个比较批次、零完整重读、同轮 Next、第二/第三次匹配审计是可调效率目标。超出目标不能单独把正确任务判失败或变成生产门禁；检查是否真有无证据空转。旧字段 `compact_continuation_fast_path_passed` 仅报告效率目标，不能等同 acceptance。错误 action、失效证据和丢失约束必须独立报告，不能被后续正确动作抹掉。

维护时在一组完整 continuation 轨迹后集中评估。不要把事后总结伪造成当时已存在的约束或证据，不读取私有思维。实际成果、成本和独立前向表现共同决定是否保留规则；细项见 [evaluation-cases.md](evaluation-cases.md)。
