---
name: task-continuity
description: 为长任务保存目标、约束、证据和下一动作，在压缩、暂停或交接后按身份恢复。普通新任务和单次定位无需恢复流程。
---

# Task Continuity

负责持续任务的状态与恢复，不重做领域设计、检索或委派。原目标、已接受约束与授权持续有效，不因压缩而重新询问。

## 保存最小主视图

覆盖更新已有任务载体或安全临时状态，无安全持久载体时使用有界 active context，交接前提供便携胶囊；不自动安装后端、建目录或改 Git 配置。

- **Contract**：任务身份、目标、契约 revision、有效约束及验收。
- **Checkpoint**：当前阶段、正在做的事、有效证据及被测源码 / 制品身份。
- **DecisionState**：已接受决定、未决分歧，以及容易重放的已完成动作与重开条件。
- **Resume**：有稳定 `action_id` 的 Next，精确落点、范围、前提、预期观察和真实阻塞；临时插入任务保留返回点。

删除过时假设和重复总结；原始日志与机器收据按需取回。运行态不进入产品、架构或 API 权威文档。

## 恢复与继续

1. 核对 task / source / contract / action 身份、最新指令及 Next 必需证据。匹配时复用锚点，直接执行 Next，不重学整个项目。
2. 失配时只刷新受影响身份、路径或证据。身份 / 权限不足不能据此实施或宣称验收，但独立读取和已授权工作可继续。
3. 问题先简答再继续；重复提醒合并约束，新约束只改变受影响范围。外部调用超时先核对原 operation 与幂等状态，不自动重放。
4. 契约实质替换时，使依赖旧契约的动作和委派验收失效；简单任务无需引入复杂 schema。

阶段末集中验证；相关源码、契约、输入与环境仍匹配时复用证据。提交 / 发布按项目和用户授权，不由恢复技能自动触发。

## 按需资料

- 冷交接、复杂失配或状态格式：[恢复协议](references/task-state-and-recovery-rules.md)，JSON schema 是可选交换格式。
- hooks / 收据配置：[宿主适配](references/host-adapters.md)。Codex execution adapter 只在显式配置后启用，不安装 hooks。
- 已有结构化状态：[验证](scripts/validate_continuity_state.py) 或 [投影](scripts/prepare_resume_context.py)，不生成目标或 Next。
- 维护与评估：[用例](references/evaluation-cases.md)、[评测器](scripts/evaluate_continuity_trace.py)、[研究](references/research-basis.md)。

报告结果、必要证据和未解决事项，不要求每轮展示胶囊或门禁字段；读取次数和响应轮数不决定正确性。
