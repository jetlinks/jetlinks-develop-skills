# 研究与工程实践依据

本文件用于审查或演进系统性求解流程，不是日常执行必读材料。下列来源只支撑方法选择，不替代当前工作区事实。

## 1. 代理技能与执行循环

- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills) 说明 skill 通过 `name` / `description` 触发，并以 `SKILL.md`、references 和可选 scripts 进行渐进披露；最佳实践包括单一职责、命令式步骤、明确输入输出和用真实 prompts 测试触发行为。因此本技能把短执行流程放在 `SKILL.md`，把判断表和例子放在 references，并保持与具体领域技能分离。
- [ReAct](https://arxiv.org/abs/2210.03629) 将推理、行动和环境观察交替进行，使计划能随新证据更新并减少错误传播。对应到本技能，是“假设 → 区分检查 → 观察 → 更新假设”，而不是先写完一串补丁再解释。
- [Reflexion](https://arxiv.org/abs/2303.11366) 使用环境反馈形成语言化反思并影响后续尝试；[Self-Refine](https://arxiv.org/abs/2303.17651) 也要求反馈先于下一轮改进。因此失败尝试必须产出“否定了什么假设”，否则不允许原模型下继续修改。

## 2. 真实软件任务与代理实现

- [SWE-bench](https://arxiv.org/abs/2310.06770) 指出真实 issue 往往需要同时理解并协调多个函数、类和文件，并与执行环境交互。复杂任务不能只盯着报错文件，必须建立跨生产者、边界和消费者的最小系统图。
- [SWE-agent 的 Agent-Computer Interface](https://swe-agent.com/latest/background/aci/) 强调为模型提供简单、信息密度高的浏览、编辑和执行反馈。其 [`agents.py`](https://github.com/SWE-agent/SWE-agent/blob/main/sweagent/agent/agents.py) 为格式错误、被阻止动作和命令错误设置有界 requery，并保存 trajectory；这支持“重试必须有边界和反馈轨迹”，但本技能进一步区分机械 requery 与根因假设失效。
- [Aider architect mode](https://github.com/Aider-AI/aider/blob/main/aider/coders/architect_coder.py) 将方案形成与文件编辑分成不同角色 / 阶段；其 [linting and testing](https://aider.chat/docs/usage/lint-test.html) 将真实 lint / test 输出反馈给后续修复。对应到本技能，是先形成问题模型和解法层级，再编辑，并用外部验收信号而非自我评价推进。

## 3. 变更与评测

- [Google Engineering Practices：Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) 强调小而自包含、易推理和易验证的变更。这里采用“最小完整改动”而非机械追求最少行数：一个自包含修复可以跨多个文件，但不能混入独立主题。
- OpenAI skill 指南要求用 prompts 检查触发边界。维护本技能时至少前向验证三类任务：主动复杂任务、从简单任务升级为停滞任务、根因明确的机械小修；同时检查是否正确联动领域技能、是否在第一次失败后重构假设、是否避免对小修过度建模。

## 4. 计划与制品生命周期依据

- [OpenAI：Long-running work](https://learn.chatgpt.com/docs/long-running-work) 将长任务的稳定入口收敛为 outcome、constraints 和 verification，并建议在同一任务上下文中持续引导；这支持让权威契约保持精简，把实时推进状态留在任务上下文，而不是逐轮追加到仓库设计文档。
- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills) 强调 focused skill、渐进披露、命令式步骤、显式输入输出和真实 prompt 测试；因此制品生命周期规则集中在 router reference，focused skills 只引用统一门禁，避免每个技能各自发明计划 / worklog 目录。
- [Git：gitignore](https://git-scm.com/docs/gitignore) 将 `$GIT_DIR/info/exclude` 定义为仓库特定但不需要共享的本地忽略规则；因此无 Trellis 的 agent runtime 兜底使用 repository-local exclude，并必须通过 `git check-ignore` 验证，而不是默认修改共享 `.gitignore`。
- 真实 Trellis 工作区表明 `.trellis/` 可能同时包含 task、research、journal、spec 和 runtime，且项目可能整体忽略、部分强制跟踪或由 finish 流程提交。因此不能把 `.trellis` 简化为“全部临时”或“全部权威”，必须读取本地 workflow、config 和 Git 策略后按 artifact 用途分流。
- OpenAI 的长任务指南同时强调同一任务上下文、明确完成标准与可验证进度。结合 Trellis “conversations get compacted; files don't” 的本地契约，恢复时应读取有界的任务检查点和精确锚点，而不是靠摘要记忆或重新扫描整个仓库。
- [Martin Fowler：Feature Branch](https://martinfowler.com/bliki/FeatureBranch.html) 将一组相关变更作为可审查集成单元；[Google Engineering Practices：Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) 强调小而自包含的逻辑变更。这支持“阶段验证后本地提交、整个单一任务完成后统一远程交付”：commit 保留可恢复阶段边界，PR 表达一个完整审查主题，而不是承担每步执行日志。

## 5. 验证证据生命周期

- Rothermel 与 Harrold 的 [A Safe, Efficient Regression Test Selection Technique](https://doi.org/10.1145/248233.248262) 将安全回归测试选择建立在变更影响关系上：只选择可能受改动影响的测试，同时保持相对全量回归的故障揭示能力。这支持先做验收矩阵与影响映射，再只补跑缺失或失效范围，而不是在 delivery 阶段无条件重跑全部测试。
- [Bazel Remote Caching](https://bazel.build/remote/caching) 以动作及其输入的哈希标识可复用结果；[Git Internals - Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) 区分保存内容的 tree 与附带父提交、作者和消息的 commit。对应到交付门禁：相关代码、测试、配置、依赖、工具链和环境输入未变时可以复用已有证据；仅创建 commit 导致 commit hash 改变但 tree 不变，不应单独触发重跑。
- 外部状态、安全 / 依赖数据和发布基线检查具有时效性，不能只靠内容指纹永久复用。证据门禁因此同时检查覆盖范围、输入指纹、base 漂移、环境等价性和检查时效性。

## 6. 从依据到规则的映射

| 依据 | 落地规则 |
| --- | --- |
| ReAct 的推理—行动—观察循环 | 每个检查都必须区分候选假设并更新计划 |
| Reflexion / Self-Refine 的反馈驱动迭代 | 失败后先记录被否定假设，不原样继续 |
| SWE-bench 的跨文件真实任务 | 扫描完整执行路径和变体，不只修报错点 |
| SWE-agent 的有界 requery / trajectory | 设置局部修补预算并保留决策证据 |
| Aider 的 architect / editor 分阶段 | 问题建模、方案选择和实现阶段分离 |
| Small CLs 的自包含变更 | 追求最小完整闭环，不混入无关重构 |
| OpenAI skills 的渐进披露与触发测试 | focused skill + 按需 references + 正反 prompts |
| Long-running work 的 outcome / constraints / verification | 权威任务契约保持精简；实时状态留在任务上下文 |
| Git repository-local exclude | 无工作流时使用已验证的本地忽略运行态，不污染共享 Git 配置 |
| Trellis 的混合 artifact 生命周期 | 按用途与本地契约分流，不以 `.trellis` 路径或 Git 状态判断权威性 |
| 有界任务检查点 + Git 指纹 | 上下文压缩后定向恢复，不重新全仓扫描或依赖模型记忆 |
| Small CL / feature branch | 阶段闭环后本地提交；完整任务统一 push / PR，不逐步远程流水 |
| 安全回归测试选择 | 将证据映射到验收矩阵，只补跑受影响或缺失的检查 |
| 输入哈希缓存 + Git tree 语义 | 以相关输入和 tree / diff 判断证据有效性，不因交付阶段或 commit 元数据机械重跑 |
