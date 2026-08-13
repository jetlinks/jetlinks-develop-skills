# 研究与工程实践依据

本文件用于审查或演进任务连续性流程，不是日常执行必读材料。

- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills) 强调 focused skill、渐进披露、命令式输入 / 输出和真实触发测试，支持把任务连续性与领域求解、代码导航拆成独立能力。
- [OpenAI：Hooks](https://learn.chatgpt.com/docs/hooks) 当前提供 `PreCompact`、`PostCompact`、`SessionStart`、`PreToolUse`、`PostToolUse`、`Stop` 等事件；根会话压缩后会在下一次模型请求前触发 `SessionStart(source=compact)`，自动压缩发生在 turn 中间时也会把附加上下文交给紧接着的 continuation。官方同时说明多个 hooks / plugins 的上下文会累积并可能降低模型表现，tool hooks 也存在未覆盖路径。这支持在宿主可用时只注入有大小上限的恢复索引和精确 `first_allowed_action`，而不反复注入技能、任务和系统图全文；hooks 仍只作为需信任审查的可选 guardrail，不能替代通用语义门禁。
- [Context as a Tool / Cat](https://arxiv.org/abs/2512.22087) 将长程软件代理上下文分为稳定任务语义、可演化长期记忆和近期高保真交互，并在阶段边界主动折叠历史；其 SWE-bench Verified 实验支持“稳定契约 + 可演化决策状态 + 近期关键观察”的模型主视图，而不是 append-only 历史或固定阈值通用摘要。
- [ACON](https://arxiv.org/abs/2510.00615) 用完整上下文成功而压缩上下文失败的成对轨迹优化压缩指南，指出长任务摘要必须保留因果关系、环境状态、前置条件和未来决策线索。这支持用 continuation 成功率和遗漏约束评测恢复胶囊，而不只检查长度或字段存在。
- [HORIZON](https://arxiv.org/abs/2604.11978) 在跨领域长程轨迹中区分 planning error、history error accumulation、catastrophic forgetting 与 memory limitation，并指出长程难度不能只按动作数定义。这支持保存长期约束、最新转折证据和可执行 next，同时对恢复后偏航做轨迹级诊断。
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) 区分 thread-scoped checkpoint 与 cross-thread store；[Temporal Workflows](https://docs.temporal.io/workflows) 以事件历史重建执行状态并在 replay 时复用已记录的 activity 结果。这些成熟系统实践支持把实时 checkpoint、长期知识与验证证据分层，并按 identity 复用已有结果。
- [Google Engineering Practices：Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) 强调小而自包含的逻辑变更，支持“连贯阶段验证后本地 checkpoint”，而不是每个操作提交。
- Rothermel 与 Harrold 的 [安全回归测试选择](https://doi.org/10.1145/248233.248262) 以变更影响关系选择可能受影响的测试，支持先映射验收矩阵再补跑失效范围。
- [Bazel Remote Caching](https://bazel.build/remote/caching) 用动作和输入摘要识别可复用结果，说明证据有效性取决于相关输入、语义和环境，而不是工作流进入了新的阶段。

维护本技能时使用 [`evaluation-cases.md`](evaluation-cases.md) 前向验证：除无文件 / 无 VCS、非 Git identity、计划收敛、阶段 checkpoint、单一 review 和证据复用外，必须覆盖验证改变路线后立即压缩、同一恢复切片连续 3–5 次压缩、空泛 `Next` 拒绝进入 `READY`、规则 revision 未变化时复用已提取义务、同 HEAD 下 untracked 内容漂移、部分指纹下实施、陈旧胶囊阻断生产修改、外部引用 revision 未变化时不完整重读、revision 变化时只取增量，以及运行态不能提升到权威文档。

上述来源支撑的是分层状态、主动阶段压缩、identity-bound replay、结果复用和轨迹评测原则。`Contract / Checkpoint / DecisionState / Resume`、`READY / SNAPSHOT_REQUIRED / RESUME_AUDIT`、默认 3–7 个 anchors，以及第二 / 第三次恢复止空转门槛是基于这些原则形成的工程协议，必须通过真实宿主轨迹调优，不能表述成论文直接规定的字段或常数。
