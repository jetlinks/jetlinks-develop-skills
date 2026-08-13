# 研究与工程实践依据

本文件用于审查或演进任务连续性流程，不是日常执行必读材料。

- [OpenAI：Build skills](https://developers.openai.com/codex/build-skills) 强调 focused skill、渐进披露、命令式输入 / 输出和真实触发测试，支持把任务连续性与领域求解、代码导航拆成独立能力。
- [OpenAI：Hooks](https://learn.chatgpt.com/docs/hooks) 当前提供 `PreCompact`、`PostCompact`、`SessionStart`、`PreToolUse`、`PostToolUse`、`Stop` 等事件；根会话压缩后会在下一次模型请求前触发 `SessionStart(source=compact)`。这些能力可用于保存状态、注入有界恢复索引以及在已覆盖的本地工具上增加门禁，但 hooks 需要宿主支持与信任审查，且不能覆盖所有专用 / 托管工具，因此只能作为可选 guardrail。
- [Google Engineering Practices：Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) 强调小而自包含的逻辑变更，支持“连贯阶段验证后本地 checkpoint”，而不是每个操作提交。
- Rothermel 与 Harrold 的 [安全回归测试选择](https://doi.org/10.1145/248233.248262) 以变更影响关系选择可能受影响的测试，支持先映射验收矩阵再补跑失效范围。
- [Bazel Remote Caching](https://bazel.build/remote/caching) 用动作和输入摘要识别可复用结果，说明证据有效性取决于相关输入、语义和环境，而不是工作流进入了新的阶段。

维护本技能时使用 [`evaluation-cases.md`](evaluation-cases.md) 前向验证：除无文件 / 无 VCS、非 Git identity、计划收敛、阶段 checkpoint、单一 review 和证据复用外，必须覆盖验证改变路线后立即压缩、同阶段连续压缩、同 HEAD 下 untracked 内容漂移、部分指纹下实施、陈旧胶囊阻断生产修改、外部引用 revision 未变化时不完整重读、revision 变化时只取增量，以及运行态不能提升到权威文档。
