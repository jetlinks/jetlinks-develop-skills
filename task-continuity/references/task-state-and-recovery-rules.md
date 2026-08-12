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

阶段切换时原位替换：移除完成 checkbox、旧操作列表、被否定假设、重复摘要和累计计数。最近完成边界只在 Recovery Capsule 的 `Validated` 字段保留一个证据指针；审计历史若确实是宿主要求，由宿主的 journal / event log 负责，不能反向膨胀当前计划。

## 4. Recovery Capsule

维护一个有界、可覆盖写的当前状态索引：

| 字段 | 内容 |
| --- | --- |
| Task | task ID / revision 或等价身份；任务契约 locator |
| Route | 当前阶段、所用能力 / skills、关键不变量或决策 |
| Validated | 最近完成阶段、验收信号、证据 locator 与其 source fingerprint |
| In-flight | 未完成阶段、是否已集中验证、预期 changed items；没有则 `none` |
| Source | workspace / source identity、复合 source fingerprint、指纹强度、预期 changed items |
| Live evidence | 仍有效的假设、最新区分证据、禁止重试的已否定路线 |
| Referenced sources | 当前路线依赖的外部 task / thread / issue / research locator、revision / cursor、已提取事实与重读条件 |
| Anchors | 恢复下一步所需的 3–7 个精确 file / symbol / resource / test / rule locator |
| Next | 一个唯一下一步及其应产生的验收信号 |
| Blockers | 需要用户、权限或外部状态决定的事项；没有则 `none` |

`source_fingerprint` 使用环境能提供的稳定身份，例如 VCS revision / tree、change-set ID、构建快照、内容摘要、artifact digest 或任务 revision。不能强制某一种实现。若工作区存在未提交或未版本化内容，指纹必须尽可能覆盖内容而不只覆盖名称或数量：

- 已版本化基线或等价 source revision。
- tracked / managed changes 的内容摘要。
- untracked / unmanaged items 的相对 locator、类型与内容摘要所形成的 manifest 摘要。
- nested workspace、submodule、generated source 或外部挂载中实际参与任务的状态摘要。
- 胶囊声明的 expected changed items，用来区分本任务变化与外部漂移。

某层不可获得时标记 `partial` 和缺失项，不能笼统声称“指纹匹配”。干净且不可变的 version / artifact identity 可以单独构成强指纹；固定 base revision 加 dirty item 数量不能。

### 外部引用账本

只为当前路线实际依赖的外部来源维护有界账本：

```yaml
ReferencedSources:
  - locator: <task / thread / issue / research resource>
    revision: <revision / cursor / updated-at / digest>
    extracted_facts: [<only facts required by Route or Next>]
    reread_when: <revision changed / fact conflicts / missing decision detail>
```

恢复时先用最轻量能力比较 revision / cursor。未变化且 `extracted_facts` 足够支撑 `Next` 时直接复用；优先使用增量 wait、delta、page cursor、change feed 或条件读取，而不是重新完整读取。来源发生变化时只读取 revision 之后的增量；只有增量无法解释冲突或定位关键事实时才扩大到历史页面。账本不保存整份外部正文或无关历史。

胶囊只保存路线索引，不复制任务全文、整张关系图、长 diff、日志、命令流水或所有已完成步骤。它应小到能在一次恢复中完整读取；引用账本与 anchors 合计仍应保持有界。

## 5. 刷新边界

只在以下边界刷新：

- 用户确认或改变任务契约。
- 根因模型、解法层级或主路线变化。
- 一个连贯阶段完成并获得验收证据。
- 准备暂停、交接、主动压缩或预计上下文即将丢失。
- 外部变化使任务身份、source fingerprint 或锚点失效。

刷新时覆盖旧状态。尚未验证的工作只能进入 `In-flight`，不能写成 `Validated`。若宿主有阶段 commit、build、snapshot 或 review ID，可作为证据 locator；通用协议不要求其中任何一种。

## 6. 恢复算法与读取预算

1. 读取用户最新指令、任务契约和 Recovery Capsule，确认任务身份、目标和唯一下一步。
2. 使用当前环境最轻量的只读能力比较复合 source fingerprint、预期 changed items，以及引用账本中的 revision / cursor。
3. 指纹和引用均匹配时，只加载宿主要求的当前 skill body、当前阶段确实需要的 rules、胶囊列出的 3–7 个 anchors，从 `Next` 继续；不重读 research basis、已提取外部历史、整个任务树或仓库总览。
4. 引用 revision 变化但 source 匹配时，先读取引用增量，更新 `extracted_facts`；不因此重新扫描源码。
5. source 部分失配时，先检查失配 changed items 或 artifact，只扩大到解释失配所需的生产者、消费者或所有权边界，并重写胶囊。
6. 任务身份、契约或 source state 无法建立时停止实施，向用户请求一个聚焦的决定；不要猜路线。

默认恢复读取预算只包含：最新指令、任务契约、胶囊、复合指纹检查、引用 revision 检查、当前阶段规则、3–7 个 anchors。任何超出预算的读取必须对应一个明确的身份 / 指纹 / 引用 / 锚点失配，并说明它将消除哪项不确定性。恢复后的第一项生产性动作必须直接服务于 `Next`；“继续读取以熟悉项目”不是生产性动作。

恢复后第一项生产性动作必须服务于胶囊的 `Next` 和验收信号。相邻 TODO、旧方案或新可用工具都不能自动扩大范围。

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

在提供版本化 checkpoint 的环境中，阶段进入 `Validated` 前必须已经创建实际本地 checkpoint，并记录其 identity；只有验证通过但尚未 checkpoint 的阶段仍为 `In-flight(validation=passed)`。checkpoint 之后若 source tree 与被测内容等价，checkpoint metadata 变化本身不使验证证据失效。

## 9. 可选宿主自动化

若宿主提供 lifecycle hooks、checkpoint callbacks 或 equivalent automation，可选择：

- 在压缩前保存有界胶囊。
- 在压缩 / 恢复后注入胶囊摘要和 locator。
- 在停止时检查是否存在唯一下一步、未映射验收项或未说明的失败。
- 在工具调用后只采集证据 locator，不把完整输出持续注入上下文。
- 用外部来源 revision / cursor 自动维护增量引用账本，未变化时不再次注入完整历史。
- 在保存前计算宿主可提供的复合 source fingerprint，并对缺失层标记 `partial`。

这些是可选适配，不是技能依赖。自动化必须有界、可审查、可禁用，不能修改问题结论、替代任务证据或把私有数据发送到未授权位置。
