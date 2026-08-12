# 任务连续性前向评测

## 目录

- [评测观察项](#评测观察项)
- [核心用例](#核心用例)
- [通过标准](#通过标准)

本文件只在维护或评测 `$task-continuity` 时读取。以真实宿主能力运行，记录实际轨迹；不要把预期答案泄漏给被测智能体，也不要为了通过用例临时注入某个文件、命令或产品名。

## 评测观察项

每条轨迹至少记录：首次生产性动作前的读取范围、是否重读完整外部历史、source fingerprint 组成及强度、anchors 数量、计划项数量、重复检查、checkpoint / publish / review 次数，以及运行态是否泄漏到权威来源。

## 核心用例

| 用例 | 输入变化 | 必须观察到 | 失败信号 |
| --- | --- | --- | --- |
| 压缩后无变化恢复 | 有 task、胶囊、强指纹、未变化的外部引用和 3–7 个 anchors | 比较身份与 revision 后直接执行 `Next`；不重扫 workspace | 重读完整 thread / research / README / 任务树，或先做相邻 TODO |
| 同 HEAD 脏树漂移 | base revision 不变，但 tracked 内容或 untracked 内容改变 | 复合指纹报告失配并只检查失配 items | 仅因 HEAD 和文件数相同就声称匹配 |
| 外部引用增量 | 源码不变，引用 task / thread revision 增加 | 读取 revision / cursor 之后的增量并更新 extracted facts | 完整重读外部历史，或因引用变化重扫源码 |
| 部分身份 | 宿主无法摘要 untracked 或 nested source | 明确标记 `partial`、缺失层和剩余风险 | 笼统声明强匹配或自行安装状态后端 |
| 阶段中途压缩 | 实现已修改但尚未集中验证或 checkpoint | 只写 `In-flight`、expected items 和唯一下一步 | 把阶段写入 `Validated` 或伪造 checkpoint identity |
| 阶段完成 | 一个连贯能力切片已验证，宿主有本地版本化 checkpoint | 创建一个本地 checkpoint 后才进入 `Validated` | 按文件 / 命令提交，或验证后无 checkpoint 却称已验证阶段 |
| 单一远程交付 | 多个阶段均有本地 checkpoint，总体验收通过 | 整个任务统一 publish，并创建或更新一个 task-level review | 每阶段 push、多个 PR、用 review 评论记流水 |
| 证据复用 | 阶段测试已覆盖最终等价 source tree，进入交付阶段 | 映射验收矩阵并直接复用，仅补缺失 / 失效项 | 仅因 commit、交付或 PR 阶段机械全量重跑 |
| 权威文档提升 | 实现阶段产生 fixture 编号、测试数量和一个稳定架构结论 | 只原位提升已确认的稳定架构结论 | 将 phase / slice / fixture / 测试进度写进权威 docs |
| 无文件或无 VCS | 宿主只有 task context 和 artifact revision | 使用可复制胶囊及现有 identity，正常降级 | 强制创建文件、Git 仓库、数据库或修改忽略规则 |

## 通过标准

- 指纹匹配恢复时，全仓扫描和未变化外部历史完整重读均为 0。
- 复合指纹对 tracked、untracked 或 nested 任一任务相关漂移的识别率为 100%；能力缺失时必须降级为 `partial`。
- current plan 不保存完成流水；anchors 保持 3–7 个；第一项生产性动作服务于唯一 `Next`。
- 每个连贯阶段最多一个本地 checkpoint；每个任务最多一个远程 review。
- 有效证据重复执行、运行态泄漏到权威来源、伪造 `Validated` 均为 0。
