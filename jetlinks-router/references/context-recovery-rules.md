# JetLinks 任务恢复适配

仅在实际压缩、暂停续作、交接或长任务状态维护需要 Git / Trellis 映射时读取。恢复状态、主线保持、动作身份和证据规则唯一来源是 [task-continuity](../../task-continuity/SKILL.md) 及其 [恢复规则](../../task-continuity/references/task-state-and-recovery-rules.md)；本文件不另建状态机或恢复次数门槛。

## 工作区映射

| 通用对象 | JetLinks 工作区映射 |
| --- | --- |
| Contract | 原任务目标、已接受约束与验收；引用现有任务契约或权威来源 |
| Checkpoint | 当前阶段、尚未完成切片、有效验证证据；有真实提交才记录 commit |
| DecisionState | 当前判断、最近证据、已否定路线；存在 SemanticFork / evidence budget 时保留其状态 |
| Resume | 精确文件 / symbol / test 锚点、保存的下一动作及观察信号 |
| Source Snapshot | 实际参与任务的 Git 工作树或其他源码载体的内容身份 |
| Continuity Metadata | 引用 / 规则 revision、授权与动作身份、证据关联 |

沿用宿主已有 task / runtime store；Trellis 项目按 [Trellis 集成](trellis-integration-rules.md) 发现本地载体。仓库 sidecar 仅在已有可写、已验证忽略的位置使用；没有安全持久载体时保留有界 active context 并在交接前输出便携胶囊。选择与清理规则见 [制品归属](document-placement-rules.md)，不自动创建目录或改 Git 配置。

## Git 身份与验证

- 干净 checkpoint 可使用 commit / tree；存在未提交变化时还需覆盖相关 tracked、untracked 和嵌套源码内容。branch、HEAD、文件数量不能代表工作树相同。
- 只纳入实际参与当前任务的源码边界；无法读取的层明确为 partial，不能宣称完整匹配。
- 内容相同但只做 staging 的操作不应使行为验证证据失效。证据绑定按通用适配器定义，不以日志中的“通过”替代终态退出结果。
- 验证、目标或源码变化是否需要刷新，以及如何重用证据，均由 task-continuity 判定；不按每次编辑重建快照。
- 用户未授权或禁止提交时，保留真实的 in-flight 验证状态；不为形成 checkpoint 自动提交。

## 接入

实际恢复在普通 router 分类之前交给 task-continuity；新符号检索不经过恢复协议。匹配时执行保存的下一动作；失配时只对账相关来源，再继续主线。进度提问或新提醒保留原目标及已接受约束，只有实质目标变更才重写任务契约。

宿主可将状态导出给 [validate_continuity_state.py](../../task-continuity/scripts/validate_continuity_state.py)。它的 `suggested_gate` 是只读诊断；事实收集、持久化和执行门禁由已配置的宿主适配负责。没有脚本或 hook 时，仍可按通用协议作有界核对。

`SemanticFork.status=OPEN` 的实施边界按 [systematic-solving](../../systematic-solving/SKILL.md) 保存和执行；已解决分叉在身份匹配时继续复用，不因恢复重复选择。
