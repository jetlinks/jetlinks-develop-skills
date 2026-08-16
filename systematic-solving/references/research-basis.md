# 研究与工程实践依据

本文件用于审查或演进系统性求解流程，不是日常执行必读材料。来源只支撑方法选择，不替代当前任务事实。

## 1. 技能与工具接口

- [OpenAI：Build skills](https://developers.openai.com/codex/build-skills) 将 skill 定义为可复用工作流，并明确 focused skill、渐进披露、命令式输入 / 输出、触发边界测试以及“优先指令，确定性步骤才用脚本”。因此通用核心不声明某台机器的工具，宿主与领域细节按需扩展。
- [SWE-agent / Agent-Computer Interface](https://arxiv.org/abs/2405.15793) 强调工具接口及高信息密度反馈会显著影响代码代理表现。这支持把检索与验证表达成稳定能力契约，而不是绑定命令名。

## 2. 证据驱动迭代与停滞止损

- [ReAct](https://arxiv.org/abs/2210.03629) 将推理、行动与观察交替，使计划能随环境证据更新并减少错误传播。对应规则是“假设 → 区分检查 → 观察 → 更新假设”。
- [Reflexion](https://arxiv.org/abs/2303.11366) 与 [Self-Refine](https://arxiv.org/abs/2303.17651) 都要求反馈先于下一轮改进。失败尝试必须说明否定或收窄了什么，否则不能在原模型下继续修改。
- [SWE-agent](https://github.com/SWE-agent/SWE-agent) 对格式、命令和工具错误采用有界反馈循环，并保留 trajectory；本技能进一步区分机械修正与根因假设失效，防止把有界重试误用成业务补丁预算。
- [Aider architect mode](https://github.com/Aider-AI/aider/blob/main/aider/coders/architect_coder.py) 将方案形成与编辑分阶段；其 [lint / test workflow](https://aider.chat/docs/usage/lint-test.html) 把真实输出反馈给下一轮。这支持先形成问题模型和解法层级，再实施并接受外部验收信号。

## 3. 真实代码任务与结构检索

- [SWE-bench](https://arxiv.org/abs/2310.06770) 表明真实 issue 通常需要协调多个函数、类和文件并与执行环境交互，复杂任务不能只盯失败文件。
- [HORIZON](https://arxiv.org/abs/2604.11978) 将长程失败区分为 planning error、history error accumulation、catastrophic forgetting、memory limitation 等机制，并观察到错误会沿依赖步骤累积；这支持按失败机制选择共享根因、执行期计划核验或约束 resurfacing，而不是对所有长任务统一追加反思 / 重试。
- [AutoCodeRover](https://arxiv.org/abs/2404.05427) 用 AST 级 class / method 搜索与测试定位缩小检索空间；[Agentless](https://arxiv.org/abs/2407.01489) 表明清晰的定位—修复—验证分阶段流程是强基线。
- [Deterministic Anchoring](https://arxiv.org/abs/2606.26979) 的 2026 研究表明，轻量结构锚点能缩短轨迹、降低跨运行方差，但收益依赖仓库规模和边方向；这支持有界、按需和置信过滤，而不是默认注入整张代码图。
- [LARGER](https://arxiv.org/abs/2605.16352) 将代码定位表达为 lexical anchor 到高置信局部结构邻域的扩展，并说明这种能力不必依赖外部图数据库或专用图界面。
- [SCIP](https://github.com/sourcegraph/scip) 提供语言无关的持久 code-navigation 索引格式；compiler / language service 能提供类型感知关系，但动态分派、代理、反射、事件与运行时注册仍需保留不确定性并用其他证据补充。

## 4. 完整改动

- [Google Engineering Practices：Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) 强调小而自包含、易推理和易验证的变更。本技能采用“最小完整改动”：可跨多个文件，但不能留下双轨契约或混入独立主题。

## 5. 从依据到规则

| 依据 | 落地规则 |
| --- | --- |
| OpenAI skills | focused 通用核心、渐进披露、真实触发测试 |
| ReAct / Reflexion / Self-Refine | 每轮由新证据更新假设；失败后先止损重构 |
| HORIZON | 对失败机制分区；规划、记忆、环境和指令问题采用不同干预 |
| SWE-bench / AutoCodeRover / Agentless | 有界定位完整路径，不全仓重读 |
| ACI | 用稳定能力和高密度 locator，避免命令与本机耦合 |
| Small CLs | 追求最小完整闭环，不追求孤立最小 diff |

维护本技能时使用 [`evaluation-cases.md`](evaluation-cases.md) 前向验证：主动复杂任务、一次失败后停滞止损、停滞后的生产修改必须有前置 Attempt、相同失败签名禁止无信息重跑、失败转移到同类场景、混合失败按生产缺陷 / 陈旧 oracle / 无效 fixture / 机械装配分区、根因明确的小修不过度建模，以及合法变化轴不会被错误抽象抹平。
