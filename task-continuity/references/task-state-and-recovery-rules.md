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

## 4. Recovery Capsule 与 Source Snapshot

维护两个有界逻辑视图。Recovery Capsule 回答“沿哪条路线继续”，Source Snapshot 回答“这些语义状态对应哪一份真实源码 / 制品”。二者可以放在同一物理 artifact，但字段、更新原因和有效性必须可区分；不能用任务摘要代替源码身份，也不能用文件摘要推断当前路线。

Recovery Capsule 是可覆盖写的当前状态索引：

| 字段 | 内容 |
| --- | --- |
| State | `READY`、`SNAPSHOT_REQUIRED` 或 `RESUME_AUDIT`，以及最近一次状态转换原因 |
| Task | task ID / revision 或等价身份；任务契约 locator |
| Route | 当前阶段、所用能力 / skills、关键不变量或决策 |
| Validated | 最近完成阶段、验收信号、证据 locator 与其 source fingerprint |
| In-flight | 未完成阶段、是否已集中验证、预期 changed items；没有则 `none` |
| Live evidence | 仍有效的假设、最新区分证据、禁止重试的已否定路线 |
| Referenced sources | 当前路线依赖的外部 task / thread / issue / research locator、revision / cursor、已提取事实与重读条件 |
| LoadedRules | 已加载 skill / rule 的 locator、revision / digest、已提取义务和需要重读的条件 |
| Anchors | 恢复下一步所需的 3–7 个精确 file / symbol / resource / test / rule locator |
| Next | 一个执行级唯一下一步：类型、精确 owner / locator 或工具动作、有界 changed items / read scope、验收信号 |
| Resume | `audit_fingerprint`、`consecutive_matching_audits`、`last_new_evidence` 与 `first_allowed_action` |
| Blockers | 需要用户、权限或外部状态决定的事项；没有则 `none` |

Source Snapshot 至少记录：source / workspace identity、复合 `source_fingerprint`、指纹强度与缺失层、expected changed items、计算该快照的边界或 locator。`source_fingerprint` 使用环境能提供的稳定身份，例如 VCS revision / tree、change-set ID、构建快照、内容摘要、artifact digest 或任务 revision。不能强制某一种实现。若工作区存在未提交或未版本化内容，指纹必须尽可能覆盖内容而不只覆盖名称或数量：

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

### 技能加载账本与执行级 Next

为当前路线确实依赖的 skill / rule 维护 `LoadedRules`：

```yaml
LoadedRules:
  - locator: <skill or rule resource>
    revision: <version / digest / updated-at>
    extracted_obligations: [<only obligations required by Route or Next>]
    reread_when: <revision changed / route now needs another section / host explicitly requires it>
```

宿主明确要求本轮完整读取某个 skill body 时必须遵守；该要求不等于重新读取它的全部 references、所有协作 skills、research basis 或项目材料。revision 未变化且已提取义务足够时，复用账本；只加载宿主强制正文、当前 `Next` 新需要的规则，或能解释已记录失配的最小片段。

`Next` 与 `first_allowed_action` 必须可直接执行，并且只能属于以下一种：

1. **生产修改**：指出 owner / file / symbol / resource、限定 expected changed items，并写出完成信号。
2. **区分检查**：指出精确工具动作或读取范围、它区分的候选，以及不同结果如何改变决策。
3. **真实阻塞**：指出缺失的权限、用户决定或外部状态，以及解除阻塞所需信号。

“继续实现某阶段”“继续分析”“熟悉代码”“再看看相关材料”不包含边界和可观察信号，不能从 `RESUME_AUDIT` 进入 `READY`。先在 `SNAPSHOT_REQUIRED` 中把它改写为执行级动作。

### 跨压缩恢复指纹

`Resume.audit_fingerprint` 对当前 task / contract revision、Source Snapshot、ReferencedSources revisions、Route / hypothesis、Anchors 和执行级 `Next` 做稳定摘要；不要把状态名、审计计数或时间戳纳入摘要。它用于识别“仍是同一个恢复切片”，不是替代各组成事实。

- 每次恢复审计与上次 `audit_fingerprint` 匹配，且其间没有生产修改、产生区分结果的检查、相关新证据或真实阻塞报告时，递增 `consecutive_matching_audits`。
- 相关 source / reference / contract、Route、hypothesis、Anchors 或 `Next` 因新事实改变时，刷新指纹并把计数重置为 `1`；仅发生上下文压缩、重新表述或重复读取不能清零。
- `last_new_evidence` 只记录最近改变决策或验收状态的 locator；没有则写 `none`。普通恢复核对不冒充新证据。
- `first_allowed_action` 必须是 `Next` 的可执行实例；它可以是一次有界 mutation、discriminating check 或 blocker report，不能是再次恢复审计或材料重读。

胶囊只保存路线索引，不复制任务全文、整张关系图、长 diff、日志、命令流水或所有已完成步骤。它应小到能在一次恢复中完整读取；引用账本与 anchors 合计仍应保持有界。

## 5. 连续性状态门禁与刷新边界

状态含义：

| 状态 | 含义 | 允许动作 |
| --- | --- | --- |
| `READY` | Task、Route、Live evidence、Source Snapshot、引用 / 规则账本和执行级 `Next` 对应同一当前事实 | 执行 `first_allowed_action` 定义的有界实现、区分检查或阻塞报告 |
| `SNAPSHOT_REQUIRED` | 新事实已经使胶囊或 Source Snapshot 不足以安全决定下一生产动作 | 只做有界只读对账、计算指纹和覆盖写运行态；禁止继续生产修改 |
| `RESUME_AUDIT` | 刚发生压缩、恢复、暂停后继续或交接，尚未证明保存状态仍对应当前事实 | 按恢复预算核验身份、引用、Route、Anchors 与 `Next`；匹配后转 `READY`，失配则转 `SNAPSHOT_REQUIRED` |

以下任一事件发生时立即进入 `SNAPSHOT_REQUIRED`，不能等到下一个“成功阶段”再补：

- 新证据改变 active hypothesis、失败签名、解法层级、验收通过 / 失败状态或唯一 `Next`。
- 用户、外部引用或权威契约的新 revision 改变当前路线依赖的事实。
- source identity 出现未声明的 changed item、nested source 漂移或预期切片之外的内容变化。
- 一个声明的 in-flight 实现切片完成、被放弃或需要换成另一切片。

同一 `READY` 状态可以授权一个预先声明、范围有界的 in-flight 实现切片；切片内 expected changed items 的连续编辑不要求每条命令刷新。若编辑暴露新根因、改变验收语义、越出 expected items 或决定改走另一条路线，则例外地立即进入 `SNAPSHOT_REQUIRED`。这使门禁约束语义变化，而不是制造新的逐操作流水账。

`SNAPSHOT_REQUIRED` 期间允许读取直接失配项、计算复合指纹、更新 Attempt / evidence、压缩计划和覆盖写胶囊；不允许继续修改生产代码、生产配置、对外契约或持久状态。刷新完成并确认 `Next` 唯一后才能回到 `READY`。

指纹为 `partial` 时可以继续只读诊断。生产修改前必须做到二选一：补齐与当前任务相关的缺失层；或明确记录无法核验的层、残余身份风险、expected changed items 和严格限定的修改范围。后者是带风险的 `READY`，不是“完整匹配”。

只在以下语义边界覆盖刷新，不在每个命令后追加：

- 用户确认或改变任务契约。
- 根因模型、解法层级或主路线变化。
- 一个连贯阶段完成并获得验收证据，或验证失败改变了失败签名、验收状态或下一步。
- 准备暂停、交接、主动压缩或预计上下文即将丢失。
- 外部变化使任务身份、source fingerprint 或锚点失效。

刷新时覆盖旧状态，并使 Recovery Capsule 与 Source Snapshot 指向同一边界。尚未验证的工作只能进入 `In-flight`，不能写成 `Validated`。若宿主有阶段 commit、build、snapshot 或 review ID，可作为证据 locator；通用协议不要求其中任何一种。

## 6. 恢复算法与读取预算

1. 压缩、恢复、暂停后继续或交接后先把状态视为 `RESUME_AUDIT`；读取用户最新指令、任务契约和 Recovery Capsule，确认任务身份、目标和执行级唯一下一步。
2. 使用当前环境最轻量的只读能力比较 Source Snapshot、预期 changed items，以及引用账本中的 revision / cursor。
3. 计算当前 `audit_fingerprint`，核对 Route、最新 evidence / Attempt、3–7 个 Anchors、LoadedRules 和 `Next` 是否彼此一致；不要仅因 source fingerprint 匹配就跳过语义核验。
4. 指纹、引用和语义状态均匹配时递增或初始化 `consecutive_matching_audits`，显式执行 `RESUME_AUDIT -> READY`，只加载宿主要求的当前 skill body 和 `Next` 新需要的规则，然后立即执行 `first_allowed_action`；不重读 research basis、已提取外部历史、整个任务树或仓库总览。
5. 引用 revision 变化但 source 匹配时转为 `SNAPSHOT_REQUIRED`，先读取引用增量并更新 `extracted_facts`；不因此重新扫描源码。
6. source 部分失配时转为 `SNAPSHOT_REQUIRED`，先检查失配 changed items 或 artifact，只扩大到解释失配所需的生产者、消费者或所有权边界，并重写两个逻辑视图。
7. 任务身份、契约或 source state 无法建立时停止实施，向用户请求一个聚焦的决定；不要猜路线。

默认恢复读取预算只包含：最新指令、任务契约、胶囊、复合指纹检查、引用 revision 检查、宿主强制规则和 `Next` 必需的少量 anchors。任何超出预算的读取必须对应一个明确的身份 / 指纹 / 引用 / 锚点失配，并说明它将消除哪项不确定性。恢复后的第一项生产性动作必须直接服务于 `Next`；“继续读取以熟悉项目”不是生产性动作。

恢复审计通过后的第一项生产性动作必须服务于胶囊的 `Next` 和验收信号。相邻 TODO、旧方案或新可用工具都不能自动扩大范围。连续匹配恢复按以下止空转门禁处理：

- 第一次允许在默认预算内完成正常审计，随后必须转 `READY`。
- 第二次且没有 `last_new_evidence` 或生产性动作时，只比较保存的组成事实与当前轻量 identity；禁止完整重读 skills / PRD / research、仓库总览或重建同一系统图，匹配后立即执行 `first_allowed_action`。
- 第三次及以后仍只有分析时，判定为空转；不能再提出“先恢复 / 再熟悉 / 下一步将实现”。本轮只能执行精确 `Next`、运行一项能区分假设的检查，或明确报告真实阻塞。

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

在提供版本化 checkpoint 的环境中，阶段进入 `Validated` 前必须已经创建实际本地 checkpoint，并记录其 identity；只有验证通过但尚未 checkpoint 的阶段仍为 `In-flight(validation=passed)`。checkpoint 之后若 source tree 与被测内容等价，checkpoint metadata 变化本身不使验证证据失效。

## 9. 可选宿主自动化

若宿主提供 lifecycle hooks、checkpoint callbacks 或 equivalent automation，可选择：

- 在压缩前保存有界胶囊与当前 Source Snapshot；保存失败时显式留下 `SNAPSHOT_REQUIRED`，不能伪装成功。
- 在压缩 / 恢复后将状态置为 `RESUME_AUDIT`，只注入胶囊摘要、source strength、`audit_fingerprint`、匹配计数、唯一 `Next` 和 locator。
- 在停止时检查是否存在执行级唯一下一步、未映射验收项、未说明的失败，或连续匹配恢复后仍只有分析动作。
- 在工具调用后只采集证据 locator，不把完整输出持续注入上下文。
- 用外部来源 revision / cursor 自动维护增量引用账本，未变化时不再次注入完整历史。
- 在保存前计算宿主可提供的复合 source fingerprint，并对缺失层标记 `partial`。
- 在宿主确实支持且覆盖目标工具时，阻止 `SNAPSHOT_REQUIRED` / 未完成 `RESUME_AUDIT` 状态下的生产修改；hook 不能覆盖的工具仍由语义门禁负责。

这些是可选适配，不是技能依赖。自动化必须有界、可审查、可禁用，不能修改问题结论、替代任务证据或把私有数据发送到未授权位置。注入内容设置严格大小上限；溢出时保存 locator 而不是把长日志或完整胶囊反复塞回上下文。
