# 研究与工程实践依据

本文件用于审查或演进任务连续性流程，不是日常执行必读材料。

- [OpenAI：Build skills](https://developers.openai.com/codex/build-skills) 强调 focused skill、渐进披露、命令式输入 / 输出和真实触发测试，支持把任务连续性与领域求解、代码导航拆成独立能力。
- [OpenAI：Hooks](https://developers.openai.com/codex/hooks) 当前提供 `PreCompact`、`PostCompact`、`SessionStart`、`Stop` 等生命周期事件，可用于保存或注入有界恢复状态；hooks 需要宿主支持、配置与信任，因此只能作为可选适配。
- [Google Engineering Practices：Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) 强调小而自包含的逻辑变更，支持“连贯阶段验证后本地 checkpoint”，而不是每个操作提交。
- Rothermel 与 Harrold 的 [安全回归测试选择](https://doi.org/10.1145/248233.248262) 以变更影响关系选择可能受影响的测试，支持先映射验收矩阵再补跑失效范围。
- [Bazel Remote Caching](https://bazel.build/remote/caching) 用动作和输入摘要识别可复用结果，说明证据有效性取决于相关输入、语义和环境，而不是工作流进入了新的阶段。

维护本技能时至少前向验证：无文件 / 无 VCS 宿主的可复制恢复、非 Git source identity、压缩后锚点恢复、计划原位收敛而不保留流水、阶段本地 checkpoint 与整体单一 review、已有有效证据在交付阶段不机械重跑。
