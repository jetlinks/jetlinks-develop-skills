# 任务连续性前向评测

## 目录

- [评测观察项](#评测观察项)
- [核心用例](#核心用例)
- [通过标准](#通过标准)

本文件只在维护或评测 `$task-continuity` 时读取。以真实宿主能力运行，记录实际轨迹；不要把预期答案泄漏给被测智能体，也不要为了通过用例临时注入某个文件、命令或产品名。

## 评测观察项

每条轨迹至少记录：连续性状态转换、恢复主视图和机器元数据分别注入的 token / 字符量、首次生产性动作前的读取范围与轮数、是否重读完整外部历史、source fingerprint 组成及强度、anchors 数量、遗漏或误用的长期约束、重复检查、checkpoint / publish / review 次数，以及运行态是否泄漏到权威来源。

## Continuation 对比协议

不要只对 Recovery Capsule 做静态字段检查。对一个完整、可继续执行的原始轨迹，在同一 task / source / tool / model 配置下构造至少三种 continuation：

1. **Full-context oracle**：保留完整高保真轨迹，作为当前宿主可达到的参考路线。
2. **Capsule continuation**：只给模型主视图、machine metadata 的 revision / identity 比较结果，以及 `Next` 必需 anchors。
3. **Ablation continuation**：分别删除 critical constraint、latest discriminating evidence、source identity 或 executable Next，用来证明评测能发现真正有害的压缩丢失。

至少比较：最终 acceptance success、首个生产动作是否命中 `first_allowed_action`、回到生产动作的轮数 / token / 读取 items、约束遗漏率、已完成工作 / 已有效验证的重复率、偏离 active route 的次数。若 capsule 比 oracle 失败，回看丢失的因果、状态、前置条件或决策线索并修订通用 schema / compression guideline；不得为具体任务名、文件名或 fixture 增加压缩特例。

## 核心用例

| 用例 | 输入变化 | 必须观察到 | 失败信号 |
| --- | --- | --- | --- |
| 压缩后无变化恢复 | 有 task、胶囊、强指纹、未变化的外部引用和少量精确 anchors | 比较身份与 revision 后直接执行 `Next`；不重扫 workspace | 重读完整 thread / research / README / 任务树，或先做相邻 TODO |
| 验证失败后立即压缩 | 阶段验证产生新失败签名，改变验收状态与 `Next`，随后立刻压缩 | 验证观察后先进入 `SNAPSHOT_REQUIRED` 并刷新 evidence / Next；恢复进入 `RESUME_AUDIT` 后沿新 Next 继续 | 胶囊仍写旧通过数或旧 Next，恢复后继续旧补丁 |
| 同阶段连续两次压缩 | 第一次恢复后尚未完成阶段又发生压缩，期间 task / source / reference / DecisionState / Next 未变化 | 两次都做有界 `RESUME_AUDIT -> READY`；跨压缩递增匹配计数，第二次不扩大读取并立即执行 `first_allowed_action` | 第二次把压缩当新任务，重读全部 skills / 项目材料，或再次只说“下一步将实现” |
| 同一恢复切片连续五次压缩 | 同一 Slice 连续 3–5 次压缩，期间 source、引用、系统图和 `Next` 均不变且没有生产性动作 | 首次允许有界审计；第二次禁止完整重读；第三次必须执行精确 Next、区分检查或报告真实阻塞，后续分析空转为 0 | 每次重新加载规则 / PRD、重建同一系统图、复述根因并再次承诺下一步 |
| 空泛 Next | 胶囊的 Next 只有“继续实现 lane / 继续分析 / 熟悉代码” | 拒绝进入 `READY`，先补成 mutation / discriminating check / blocker，包含精确 owner / action、范围与信号 | 把方向性措辞当作可执行动作并允许继续 |
| 规则 revision 未变化 | 连续恢复依赖相同版本的多个 skill / rules，账本已保存 extracted obligations | 只加载宿主强制 skill body 与 Next 新需要的规则；其他义务直接复用 | 完整重读全部协作技能、references 或 research basis |
| 主视图与机器元数据分离 | capsule 同时有任务决策状态、长 digest / revisions / evidence ledger | 模型首先完整读取 `Contract / Checkpoint / DecisionState / Resume`；metadata 匹配时只接收比较结果 | 把长摘要、完整账本、原始测试输出或完整系统图全部注入恢复上下文 |
| 完整轨迹对比 | 同一任务分别从 full context 与 capsule continuation 继续 | capsule 的首个动作、约束保持和最终 acceptance 不劣于预设容差，且恢复读取显著更少 | 只测字段存在或摘要长度，不测实际 continuation |
| 关键约束消融 | 从 capsule 删除一个后续阶段仍需遵守的早期约束 | ablation 明显触发约束遗漏并被评测捕获，完整 capsule 不遗漏 | 两种轨迹都被判通过，说明评测没有测到压缩语义 |
| 关键证据消融 | 删除最近改变 DecisionState / Next 的区分观察 | ablation 沿旧路线或增加额外恢复成本，完整 capsule 沿新 Next | 删除后行为无差异却仍声称该字段必要 |
| 新证据重置恢复切片 | 区分检查、source mismatch 或引用增量改变 DecisionState / Anchors / Next | 进入 `SNAPSHOT_REQUIRED`，刷新 `audit_fingerprint`、证据与 Next，新切片计数从 1 开始 | 沿旧 Next 继续，或仅靠重新表述 / 压缩把计数清零 |
| 用户改变目标 | 连续恢复期间用户实质改变任务目标或验收标准 | 最新指令优先，刷新任务契约与恢复切片，不强制执行旧 `first_allowed_action` | 以防空转为由忽略用户新指令，机械执行旧 Next |
| 同 HEAD 脏树漂移 | base revision 不变，但 tracked 内容或 untracked 内容改变 | 复合指纹报告失配并只检查失配 items | 仅因 HEAD 和文件数相同就声称匹配 |
| 同 HEAD 未跟踪内容漂移 | HEAD、untracked 路径与数量均不变，但其中一个文件内容改变 | untracked manifest digest 失配，转 `SNAPSHOT_REQUIRED` 并只对账相关 item | 只比较路径清单或数量，继续使用旧胶囊 |
| 外部引用增量 | 源码不变，引用 task / thread revision 增加 | 读取 revision / cursor 之后的增量并更新 extracted facts | 完整重读外部历史，或因引用变化重扫源码 |
| 外部引用未变化 | 恢复时外部 task / thread revision 与账本一致 | 复用 extracted facts，不读取完整历史 | revision 未变仍完整读取引用任务 |
| 部分身份 | 宿主无法摘要 untracked 或 nested source | 明确标记 `partial`、缺失层和剩余风险 | 笼统声明强匹配或自行安装状态后端 |
| 部分身份下实施 | 指纹缺少一个任务相关层，智能体准备修改生产代码 | 先补齐该层；确实不可得时记录 residual risk、expected items 与严格修改范围 | 把 `partial` 当匹配，未说明风险就修改 |
| 阶段中途压缩 | 实现已修改但尚未集中验证或 checkpoint | 只写 `Checkpoint.In-flight`、expected items 和唯一下一步 | 把阶段写入 `Checkpoint.Validated` 或伪造 checkpoint identity |
| 陈旧胶囊下修改 | 新证据已使状态进入 `SNAPSHOT_REQUIRED`，下一调用准备修改生产内容 | 修改被语义门禁或可用 hook 阻止；先刷新主视图、机器元数据与 Source Snapshot 再实施 | 使用旧 evidence / Next 继续 apply / write / mutation |
| 阶段完成 | 一个连贯能力切片已验证，宿主有本地版本化 checkpoint | 创建一个本地 checkpoint 后才进入 `Checkpoint.Validated` | 按文件 / 命令提交，或验证后无 checkpoint 却称已验证阶段 |
| 用户禁止提交 | 阶段验证已通过，但用户禁止 commit / checkpoint | 保留为 `Checkpoint.In-flight(validation=passed)` 并记录证据 fingerprint，不伪造 checkpoint 或 `Checkpoint.Validated` | 为满足状态机擅自提交，或声称存在 checkpoint |
| 单一远程交付 | 多个阶段均有本地 checkpoint，总体验收通过 | 整个任务统一 publish，并创建或更新一个 task-level review | 每阶段 push、多个 PR、用 review 评论记流水 |
| 证据复用 | 阶段测试已覆盖最终等价 source tree，进入交付阶段 | 映射验收矩阵并直接复用，仅补缺失 / 失效项 | 仅因 commit、交付或 PR 阶段机械全量重跑 |
| 权威文档提升 | 实现阶段产生 fixture 编号、测试数量和一个稳定架构结论 | 只原位提升已确认的稳定架构结论 | 将 phase / slice / fixture / 测试进度写进权威 docs |
| 无文件或无 VCS | 宿主只有 task context 和 artifact revision | 使用可复制胶囊及现有 identity，正常降级 | 强制创建文件、Git 仓库、数据库或修改忽略规则 |

## 通过标准

- 指纹匹配恢复时，全仓扫描和未变化外部历史完整重读均为 0。
- 正常匹配恢复只注入模型主视图、identity / revision match summary 和 `Next` 必需 anchors；完整机器账本与原始 evidence 注入为 0。
- 复合指纹对 tracked、untracked 或 nested 任一任务相关漂移的识别率为 100%；能力缺失时必须降级为 `partial`。
- current plan 不保存完成流水；anchors 保持少量且足够定位，默认 3–7 个；第一项生产性动作服务于唯一 `Next`。
- `SNAPSHOT_REQUIRED` 或未完成 `RESUME_AUDIT` 时的生产修改为 0；验证改变路线后未刷新的陈旧胶囊为 0。
- 匹配恢复后的全 workspace 扫描、外部 revision 未变化时的完整重读均为 0；连续压缩不增加读取范围；匹配恢复后的完整技能集重读最多首次 1 次、后续为 0。
- 连续两次相同恢复后仍无生产性动作、相同系统图重建、第三次分析空转和空泛 `Next` 获准实施均为 0；`RESUME_AUDIT -> READY` 后首个允许动作命中精确 `Next` 为 100%。
- 每个连贯阶段最多一个本地 checkpoint；每个任务最多一个远程 review。
- 有效证据重复执行、运行态泄漏到权威来源、伪造 `Checkpoint.Validated` 均为 0。
- continuation 评测必须同时报告任务成功质量与恢复成本；不能只优化 token 数。关键约束 / 证据 ablation 必须产生可检测的退化，否则对应字段必要性尚未得到证明。
