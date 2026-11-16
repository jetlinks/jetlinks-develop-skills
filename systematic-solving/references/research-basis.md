# 研究与工程实践依据

本文件用于审查或演进系统性求解流程，不是日常执行必读材料。来源只支撑方法选择，不替代当前任务事实。

## 1. 技能与工具接口

- [OpenAI：Build skills](https://developers.openai.com/codex/skills) 将 skill 定义为可复用工作流，并明确 focused skill、渐进披露、清晰步骤、触发边界测试以及“优先指令，确定性步骤才用脚本”。因此通用核心不声明某台机器的工具，宿主与领域细节按需扩展。
- [SWE-agent / Agent-Computer Interface](https://arxiv.org/abs/2405.15793) 强调工具接口及高信息密度反馈会显著影响代码代理表现。这支持把检索与验证表达成稳定能力契约，而不是绑定命令名。

## 2. 证据驱动迭代与停滞止损

- [ReAct](https://arxiv.org/abs/2210.03629) 将推理、行动与观察交替，使计划能随环境证据更新并减少错误传播。对应规则是“假设 → 区分检查 → 观察 → 更新假设”。
- [Reflexion](https://arxiv.org/abs/2303.11366) 与 [Self-Refine](https://arxiv.org/abs/2303.17651) 研究反馈驱动的迭代，其中 Self-Refine 使用模型自身反馈；它们不直接要求每轮都有外部证据。本技能结合 CRITIC 和真实工程任务，采用“改变根因判断须有可核验观察”的约束，不将自我反思等同于事实。
- [CRITIC](https://arxiv.org/abs/2305.11738) 说明工具提供的外部反馈能帮助模型纠错；[Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) 则表明缺少外部反馈的内在自我纠正可能退化。这支持把“反思”与“区分证据”分开，只有绑定真实观察的反馈才能授权下一轮解法。
- [Diagnosis Before Recovery](https://arxiv.org/abs/2608.11772) 提出先诊断失败类型、再选择有界恢复接口，而不是失败后统一扩展上下文或恢复动作。该 2026 预印本支持观察结果分型与选择性干预，但具体阈值仍需本技能自己的跨领域轨迹评测确定。
- [SWE-agent](https://github.com/SWE-agent/SWE-agent) 对格式、命令和工具错误采用有界反馈循环，并保留 trajectory；本技能进一步区分机械修正与根因假设失效，防止把有界重试误用成业务补丁预算。
- [Aider architect mode](https://github.com/Aider-AI/aider/blob/main/aider/coders/architect_coder.py) 将方案形成与编辑分阶段；其 [lint / test workflow](https://aider.chat/docs/usage/lint-test.html) 把真实输出反馈给下一轮。这支持先形成问题模型和解法层级，再实施并接受外部验收信号。

这些来源能支持“观察必须服务明确决策、失败先分类、方案与实施分阶段、轨迹需要检查停止行为”，但没有证明固定 Scout 数量或某类产品选择应由技术证据决定。因此，本技能把“两项默认预算”和 `SemanticFork` 字段视为需要跨领域轨迹评测的工程协议；`evidence_can_decide` 仍由当前任务的不变量与授权边界判断，不能用文献替用户选择。

## 3. 真实代码任务与结构检索

- [SWE-bench](https://arxiv.org/abs/2310.06770) 表明真实 issue 通常需要协调多个函数、类和文件并与执行环境交互，复杂任务不能只盯失败文件。
- [HORIZON](https://arxiv.org/abs/2604.11978) 将长程失败区分为 planning error、history error accumulation、catastrophic forgetting、memory limitation 等机制，并观察到错误会沿依赖步骤累积；这支持按失败机制选择共享根因、执行期计划核验或约束 resurfacing，而不是对所有长任务统一追加反思 / 重试。
- [AgentLens](https://arxiv.org/abs/2607.06624) 与 [ATOBench](https://arxiv.org/abs/2608.12996) 强调从完整轨迹检查动作、证据恢复、停止和报告链路，而不是只看最终成功位。它们是 2026 预印本，因此这里只采用“过程证据必须可观察”的方法方向，不把其领域分类写入通用规则。
- [AutoCodeRover](https://arxiv.org/abs/2404.05427) 用 AST 级 class / method 搜索与测试定位缩小检索空间；[Agentless](https://arxiv.org/abs/2407.01489) 表明清晰的定位—修复—验证分阶段流程是强基线。
- [Deterministic Anchoring](https://arxiv.org/abs/2606.26979) 的 2026 研究表明，轻量结构锚点能缩短轨迹、降低跨运行方差，但收益依赖仓库规模和边方向；这支持有界、按需和置信过滤，而不是默认注入整张代码图。
- [LARGER](https://arxiv.org/abs/2605.16352) 将代码定位表达为 lexical anchor 到高置信局部结构邻域的扩展，并说明这种能力不必依赖外部图数据库或专用图界面。
- [SCIP](https://github.com/sourcegraph/scip) 提供语言无关的持久 code-navigation 索引格式；compiler / language service 能提供类型感知关系，但动态分派、代理、反射、事件与运行时注册仍需保留不确定性并用其他证据补充。

## 4. 完整改动

- [Google Engineering Practices：Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) 强调小而自包含、易推理和易验证的变更。本技能采用“最小完整改动”：可跨多个文件，但不能留下双轨契约或混入独立主题。
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) 强调尽早校验外部输入，并区分语法与语义校验。“明确校验 owner、避免已保证条件重复校验”是本包的工程取舍，不能解释为跨独立信任边界永远只校验一次；具体校验规则由对应领域约定拥有。
- [Google Testing Blog：Test Behavior, Not Implementation](https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html) 强调测试可观察行为而非实现细节。这支持从已确认行为与风险变化选择测试，禁止为了补测试分类反向创造生产分支。

这些来源不要求逐 guard 的证据台账。校验是否必要应由当前可达信任边界、已确认契约和真实风险直接决定；无法直接建立时默认不新增，而不是继续调查以证明省略合理。

## 5. 从依据到规则

| 依据 | 落地规则 |
| --- | --- |
| OpenAI skills | focused 通用核心、渐进披露、真实触发测试 |
| ReAct / Reflexion / Self-Refine / CRITIC | 反馈驱动迭代；本包要求根因判断由可核验观察更新，不将自我反馈视为事实 |
| Cannot Self-Correct / Diagnosis Before Recovery | 内在反思不冒充证据；先诊断观察有效性，再选择恢复干预 |
| AgentLens / ATOBench | 同时评测最终结果与观察—决策—停止轨迹；证据足够后继续搜索是可测偏差 |
| HORIZON | 对失败机制分区；规划、记忆、环境和指令问题采用不同干预 |
| SWE-bench / AutoCodeRover / Agentless | 有界定位完整路径，不全仓重读 |
| ACI | 用稳定能力和高密度 locator，避免命令与本机耦合 |
| Small CLs | 追求最小完整闭环，不追求孤立最小 diff |
| Aider architect mode | 在候选契约被合法选择后再从方案进入编辑；不能用实现活动替代契约决定 |
| OWASP Input Validation + 项目工程取舍 | 在真实信任边界和不变量 owner 处负责校验，避免内部重复保证已成立的条件 |
| Test Behavior, Not Implementation | 测试由可观察行为与真实风险驱动，不能为测试分类制造生产 guard |

维护本技能时使用 [`evaluation-cases.md`](evaluation-cases.md) 前向验证：主动复杂任务、一次失败后停滞止损、停滞后的生产修改必须有前置 Attempt、相同失败签名禁止无信息重跑、失败转移到同类场景、混合失败按生产缺陷 / 陈旧 oracle / 无效 fixture / 机械装配分区、根因明确的小修不过度建模，以及合法变化轴不会被错误抽象抹平。
