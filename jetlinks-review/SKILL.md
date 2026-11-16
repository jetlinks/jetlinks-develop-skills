---
name: jetlinks-review
description: 审查 JetLinks 代码、PR 或方案中的职责混乱、模块依赖、过度设计与校验、魔法值、语义不清、响应式事务和并发、数据权限及场景特调问题。沿真实调用路径给出可核验发现，引用对应开发技能的权威规则并保留合理反例。
---

# JetLinks Review

审查实际行为、职责和契约，找出影响正确性、可维护性或平台一致性的问题。开发规则由下表中的技能拥有；本技能负责选择审查切片、收集证据和判断问题是否成立，不另建一套开发规范。

## Workflow

1. 确认审查对象、基线、目标版本和范围。PR 对比 base，工作树区分已提交与未提交变化；方案审查只能评价已给出的设计。用户要求整体审查时，沿入口、契约、状态和副作用扩展到相关模块，不止读 diff，也不默认扫描整个仓库。
2. 从变化的行为选最少规则，沿调用方 → 当前实现 → 框架 / 提供方核实职责、授权、事务和执行时机。相邻代码是事实，不能替不合理的旧实现背书；已有有效证据直接复用。
3. 用 [证据与判定方法](references/review-method.md) 区分真实缺陷、维护问题、待核实疑点和个人偏好。提出问题前检查合理反例；没有证据时继续定点取证或说明不确定性，不将关键词命中当结论。
4. 按影响排序，给出触发条件、准确代码位置、实际后果和共同根因层的修复方向。纯审查不默认修改代码；用户已授权修复时，回到规则 owner 实现最小完整变化。
5. 在连贯阶段结束后集中验证。规则 / 文档检查不能证明业务正确；历史会话中的测试结果不能作为当前分支已验证的证据。未执行必要运行检查时说明覆盖缺口。

## 按问题选择规则 owner

| 需要判断的问题 | 开发规则 |
| --- | --- |
| 应用直接依赖 device-manager、authentication-manager 等平台实现，跨服务调用 | [应用与平台边界](../jetlinks-boundary/references/application-platform-rules.md)、[命令调用](../jetlinks-boundary/references/cross-service-call-rules.md) |
| 扩展标准实体字段，2.21 注解声明或旧版中间表 | [字段扩展版本边界](../jetlinks-boundary/references/application-platform-rules.md#标准实体字段扩展) |
| 组件 / 模块职责、依赖方向、过度抽象、命名、魔法值、特调与初始化 | [职责、语义与通用性](../jetlinks-conventions/references/responsibility-and-generality-rules.md)；模块落点另见 [模块创建](../jetlinks-routing/references/module-creation-rules.md) |
| 过度校验、重复查询、状态不变量 | [CRUD 校验 owner](../jetlinks-crud/references/common-crud-rules.md#校验范围与变化语义) |
| 响应式包装、操作符堆积、事务内并发、flatMap 并发与预取 | [响应式实践](../jetlinks-reactive/references/reactive-practice.md)，重点核对订阅时机、上下文、数据规模和连接使用 |
| tenantId 等场景字段、功能 / 数据权限、独立入口或命令授权 | [AssetsHolder 统一契约](../jetlinks-assets-permission/references/assets-holder-rules.md) |
| 前端职责、组件复用、状态或交互设计 | [jetlinks-web](../jetlinks-web/SKILL.md) 的对应章节，不将后端层次机械套到组件 |
| 未发布兼容、注释、SPI、追踪或常驻资源 | [conventions](../jetlinks-conventions/SKILL.md) 与 [发布边界](../jetlinks-delivery/references/git-and-pr-rules.md#pr-内未发布变更的兼容性)，只检查涉及部分 |

需要解释规则依据时查 [资料与适用边界](references/design-sources.md)；维护技能时用 [正反场景](references/evaluation-cases.md) 走查。不要求普通审查先读完全部技能。

## 输出

- 优先报告可行动发现，按仓库已有严重性约定排序；每项包含位置、触发、影响与修复方向，同一根因不拆成多条凑数量。
- 行为 / 安全缺陷与可维护性改进分别说明；后者应解释职责泄漏、修改扩散、重复 I/O 或语义歧义的具体成本，不假装已有线上故障。
- 没有实质问题时直接说明，并交代真实审查范围和未验证边界。规则引用、检查项数量、文件行数或命名偏好都不能单独证明有缺陷。
- 不因“整体审查”增加无关构建、重写或发布动作。提交与 PR 仅在用户授权后交给 [delivery](../jetlinks-delivery/SKILL.md)。
