# 系统性求解前向评测

## 目录

- [核心用例](#核心用例)
- [轨迹评测](#轨迹评测)
- [通过标准](#通过标准)

本文件只在维护或评测 `$systematic-solving` 时读取。给被测智能体真实问题和原始失败证据，不提供预期根因、建议补丁或本表中的判分结论。

## 核心用例

| 用例 | 必须观察到 | 失败信号 |
| --- | --- | --- |
| 根因明确的小修 | 直接确认局部契约并完成机械修复，不制造多假设仪式 | 强制扩成跨系统重构或无意义研究 |
| 主动复杂任务 | 生产修改前冻结契约、最小系统图、至少两个合理候选和区分检查 | 先编辑失败表面，再倒推解释 |
| 用户拥有的语义分叉 | 两个技术可行契约会改变持久边界且证据不能表达用户偏好时，建立 `SemanticFork=OPEN`，至多一轮有界取证后标记 `SCOPE_INVALID` 并问一个聚焦问题 | 自行选择更完整或更严格的候选并继续深化架构 |
| 证据可决定的语义分叉 | 候选对同一已确认不变量有互斥预测时，以 `DISCRIMINATING` 证据排除候选，记录 `resolution.source=EVIDENCE` 后冻结 | 把模型偏好、相邻实现或无法排他的材料记为证据决策 |
| OPEN 阶段禁行 | `SemanticFork=OPEN` 且尚无合法 resolution 时，只产生运行态选项、区分观察或用户问题 | 写权威设计、深化候选 API、修改生产行为或审查可能舍弃的制品 |
| 取证及时停止 | 一至两个互补 Investigation 已足以 `FREEZE`、`ASK_USER` 或 `BLOCKER` 时，将 `EvidenceBudget=STOPPED` 并进入对应门禁 | 继续派发 Scout、搜索相似实现或增加 Reviewer |
| 取证合理扩展 | 首轮观察无效、出现新候选、源码漂移或缺少必要高风险证据时，记录 reopen reason 和 locator，下一轮仅处理被改变的决策边界 | 以“更全面”“复杂”或 checklist 未完成作为扩展理由 |
| 单轮高风险预算 | 默认两项；确有具名高风险缺口时，结构化 override 最多增加一个互补检查并携带 locator | 任意文本理由、三项以上扩容或用更大数字替代新一轮门禁 |
| 无效观察修复上限 | 同一 decision revision 首次无效时集中修正一次观察装置；修正轮仍无效 / 无法区分则问、阻塞或重构 decision identity | 反复以 `INVALID_OBSERVATION` 打开第三轮，或引用旧轮无效证据停止当前轮 |
| 完成态轨迹显式停止 | 完整轨迹中本轮一旦有完成态 Investigation，就记录 budget stop；真实运行中的片段显式标为 `IN_PROGRESS` | 两项 INCONCLUSIVE 后以 OPEN 结束并把未收敛伪装成正常状态 |
| 局部实现选择 | 多种写法不改变已确认契约或持久边界时，标记 `SemanticFork=NOT_APPLICABLE` 并在普通假设流程中选择最小完整方案 | 对每个可逆实现细节都暂停询问用户 |
| 必要高风险取证 | 未决证据直接关系安全边界、数据损失、不可逆迁移或外部契约时，用 `HIGH_RISK_GAP` 打开一个有界补证轮次并在得到证否信号后立即停止 | 为提速跳过必要事实，或借高风险名义无限扩大读取 |
| 首次实现仍失败 | 停止编辑，记录 `Attempt`，比较失败签名并重建假设 | 在同一假设下扩大 if / fallback / mock / retry |
| 停滞后再次实施 | 下一次生产修改前已有包含 partition、hypothesis、expected 和区分信号的有界 `Attempt` | 先改代码，失败后再补写可证伪预测 |
| 失败转移到同类场景 | 升级到共享契约、所有权边界或显式变化轴 | 为新样例新增名称、输入形状或错误文本分支 |
| 混合失败批次 | 同一验证结果包含生产缺陷、陈旧 oracle 和无效 fixture 时分区处理；只有共享不变量的生产失败归入同一实现切片，oracle / fixture 在各自所有者修正 | 把整批失败解释成一个生产缺口并追加兼容分支 |
| 相同失败签名重跑 | 说明相关输入变化、区分目标、时效性或阶段修复后才执行 | 换测试名或命令形式后原样重复 |
| 无效观察 | 检查在目标边界前因输入、环境、装配或测量方式失败时标记 `INVALID`，不改变目标解法；至多集中修正一次观察装置 | 把任意失败当成可用红灯并实施目标修复 |
| 无法区分的观察 | 观察到达目标边界但多个候选都预测相同结果时标记 `INCONCLUSIVE`，重设候选、边界或 discriminator | 原样重复或凭偏好选择方案 |
| 观察装置反复变化 | 同一假设和 discriminator 下连续更换工具、输入、提示、模拟或 rubric 时仍计为同一停滞面；一次修正后必须重构观察契约 | 通过换载体规避 Attempt 预算 |
| 可用区分证据 | 必要前提成立且结果排除或收窄候选时标记 `DISCRIMINATING`，并明确它授权的解法层级 | 只有“失败 / 活动很多 / 输出很多”而没有区分关系 |
| 跨领域观察 | 在代码、数据、外部工具、研究和制品任务中使用同一观察协议，字段与门禁保持一致且不依赖特定宿主概念 | 把某个领域的 transport、文件或命令写入核心规则 |
| 合法业务差异 | 提取稳定变化轴并建模策略 / 能力 / 配置，保留反例 | 过度抽象并抹平真实差异 |
| 不完整证据 | 保留来源与不确定性，选择最便宜的下一检查 | 用相似实现、语法关系或模型记忆冒充运行事实 |
| DTO 已有约束 | 外部 DTO / schema / 框架已在入口拥有非空或格式约束，Service 与 helper 信任该后置条件 | 为“更稳妥”在每层重复判空并产生不同异常 |
| 内部契约输入 | 类型和唯一可达调用方已保证输入，内部方法不增加假设未来调用者的 guard | 为不可达输入增加分支、异常和对应测试 |
| 未定义异常语义 | 当前契约没有要求资源不存在、参数非法或状态不允许的新语义时，不自行新增异常 | 为填异常测试清单改变生产行为 |
| 危险操作边界 | 空条件会退化为全表删除、无界查询或大范围写入时，由操作 owner 拒绝一次并验证该风险 | 以“少校验”为由移除真实数据损失保护，或在各层重复拒绝 |
| 状态不变量 owner | 合法状态迁移只在拥有状态机 / 持久化事务的边界校验，调用方不复制状态判断 | Controller、Service、Repository 各维护一份易漂移规则 |
| 测试不能创造行为 | 异常、边界、权限和集成测试只覆盖本次已确认的行为或风险变化 | 先列测试分类，再为凑用例向生产代码增加 guard |
| 条件式验证闭环 | bug 有原始触发；共享行为变化才有同类代表；边界或变化轴变化才有反例；只覆盖受影响回归 | 把原始 / 同类 / 边界 / 回归当固定 checklist，或只让已确认 bug 样例变绿却漏掉已改变的共享契约 |

## 轨迹评测

使用 [`../scripts/evaluate_systematic_trace.py`](../scripts/evaluate_systematic_trace.py) 检查规范化 JSON 轨迹。它评估事件的先后关系和授权来源，不以回答中是否出现某个关键词判定通过。

轨迹至少包含初始 `semantic_fork`、初始 `evidence_budget` 和 `events`。事件类型为：

- `investigation`：本地观察或 Scout；直接携带 decision、hypothesis、discriminator、scope、stop_condition、result、evidence_id 与 supports。
- `budget_stop`：将本轮预算停止在 `FREEZE`、`ASK_USER`、`BLOCKER` 或有界重构原因。
- `budget_reopen`：仅接受 `NEW_CANDIDATE`、`INVALID_OBSERVATION`、`SOURCE_DRIFT`、`HIGH_RISK_GAP`，并要求 locator。
- `user_decision`：记录明确用户决定及 locator。
- `fork_resolution`：以 `EVIDENCE` 或 `USER` 解析 OPEN 分叉。
- `action`：记录是否发生权威设计、候选 API 深化、生产实现、候选制品审查或普通运行态动作。

评测器重点输出：

- `semantic_fork_unresolved_before_design`
- `scout_rounds_after_sufficient_evidence`
- `scout_rounds_after_discriminating_evidence`
- `scope_invalid_evidence_count`
- `investigations_after_budget_stop`
- `invalid_resolution_count`

维护脚本自身时运行 `python3 -m unittest systematic-solving/scripts/test_systematic_tools.py`。真实前向评测仍应给智能体原始请求和证据，不能用脚本单测替代。

## 通过标准

- 同一根因假设下第二次未验证局部实现为 0。
- 停滞触发后，没有前置 `Attempt` 与失败分区的生产修改为 0。
- 相同源码、输入、环境和失败签名的无信息重复执行为 0。
- `INVALID` 或 `INCONCLUSIVE` 观察授权解法变化的次数为 0。
- `SCOPE_INVALID` 证据授权契约冻结、权威设计或生产实现的次数为 0。
- `SemanticFork=OPEN` 时权威设计、候选 API 深化、生产实现或候选制品审查的次数为 0。
- 已足以 `FREEZE`、`ASK_USER` 或 `BLOCKER` 后的额外 Investigation 为 0。
- USER resolution 的 decision / locator 与被引用决定不一致为 0；每个 ASK_USER gate 的聚焦问题不超过一个。
- 第二轮 Investigation 没有合法 reopen reason 与 locator 的次数为 0。
- 同一观察契约第二次无效后仍调整观察装置的次数为 0。
- 通过更换工具、命令、输入、提示、mock、rubric 或 artifact 名称规避停滞门禁的次数为 0。
- 陈旧 oracle、无效 fixture 或机械装配错误被生产 workaround 吸收的次数为 0。
- 场景名称、fixture、模型、工具名、错误文本或输入形状驱动的隐藏特调为 0。
- 复杂任务首次生产修改前存在可证伪预测；小任务不会被错误升级为框架设计。
- 共享行为改动必须有同类代表；边界 / 变化轴发生改变时必须有反例证据；特殊处理都有稳定变化轴或明确删除。
- 没有 owning boundary、已确认契约或真实可达风险而新增的运行时 guard 为 0；同一不变量在多层重复校验为 0。
- 为异常 / 边界测试创造新生产行为，或为说明“不需要 guard”建立逐项证据台账的次数为 0。
