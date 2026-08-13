# 研究与工程实践依据

本文件用于审查或演进任务连续性流程，不是日常执行必读材料。

- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills) 强调 focused skill、渐进披露、命令式输入 / 输出和真实触发测试，支持把任务连续性与领域求解、代码导航拆成独立能力。
- [OpenAI：Hooks](https://learn.chatgpt.com/docs/hooks) 当前提供 `PreCompact`、`PostCompact`、`SessionStart`、`PreToolUse`、`PostToolUse`、`Stop` 等事件；根会话压缩后会在下一次模型请求前触发 `SessionStart(source=compact)`，自动压缩发生在 turn 中间时也会把附加上下文交给紧接着的 continuation。官方同时说明多个 hooks / plugins 的上下文会累积并可能降低模型表现，tool hooks 也存在未覆盖路径。这支持在宿主可用时只注入有大小上限的恢复索引和精确 `first_allowed_action`，而不反复注入技能、任务和系统图全文；hooks 仍只作为需信任审查的可选 guardrail，不能替代通用语义门禁。
- [Google Engineering Practices：Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) 强调小而自包含的逻辑变更，支持“连贯阶段验证后本地 checkpoint”，而不是每个操作提交。
- Rothermel 与 Harrold 的 [安全回归测试选择](https://doi.org/10.1145/248233.248262) 以变更影响关系选择可能受影响的测试，支持先映射验收矩阵再补跑失效范围。
- [Bazel Remote Caching](https://bazel.build/remote/caching) 用动作和输入摘要识别可复用结果，说明证据有效性取决于相关输入、语义和环境，而不是工作流进入了新的阶段。

维护本技能时使用 [`evaluation-cases.md`](evaluation-cases.md) 前向验证：除无文件 / 无 VCS、非 Git identity、计划收敛、阶段 checkpoint、单一 review 和证据复用外，必须覆盖验证改变路线后立即压缩、同一恢复切片连续 3–5 次压缩、空泛 `Next` 拒绝进入 `READY`、规则 revision 未变化时复用已提取义务、同 HEAD 下 untracked 内容漂移、部分指纹下实施、陈旧胶囊阻断生产修改、外部引用 revision 未变化时不完整重读、revision 变化时只取增量，以及运行态不能提升到权威文档。
