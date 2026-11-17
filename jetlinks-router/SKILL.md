---
name: jetlinks-router
description: 为入口不明确的 JetLinks 任务选择最少的相关技能。已选中正确领域技能时直接继续，无需重新路由。
---

# JetLinks Router

只负责选择入口，不执行另一套设计、恢复或审查流程。按当前动作选择技能，背景里出现某个技术名不构成加载理由。

## Routing

| 当前动作 | 入口及职责 |
| --- | --- |
| 找定义、调用链、依赖证据或变更影响 | [code-navigation](../code-navigation/SKILL.md)：检索与证据 |
| 判断模块归属、发现工作区或创建模块 | [jetlinks-routing](../jetlinks-routing/SKILL.md)：代码落点 |
| 应用依赖平台、字段与对象关系建模、语义声明、跨服务命令 | [jetlinks-boundary](../jetlinks-boundary/SKILL.md)：交互契约 |
| 实体、查询、写入、批量或状态动作 | [jetlinks-crud](../jetlinks-crud/SKILL.md)：数据行为 |
| 资产实体声明、AssetsHolder、关联资产或独立入口授权 | [jetlinks-assets-permission](../jetlinks-assets-permission/SKILL.md)：数据权限 |
| 生命周期事件、消息投递、Topic 或持续订阅 | [jetlinks-events](../jetlinks-events/SKILL.md)：触发与交付语义 |
| Mono / Flux、事务连接、并发或背压 | [jetlinks-reactive](../jetlinks-reactive/SKILL.md)：执行与资源控制 |
| 设备协议、传输编解码、认证或应答关联 | [jetlinks-protocol](../jetlinks-protocol/SKILL.md)：报文契约 |
| 职责、语义、通用策略、运行状态或编码规范 | [jetlinks-conventions](../jetlinks-conventions/SKILL.md)：共享开发规则 |
| Vue 页面、交互、组件或前端状态 | [jetlinks-web](../jetlinks-web/SKILL.md)：前端实现 |
| 审查代码、PR 或方案 | [jetlinks-review](../jetlinks-review/SKILL.md)：取证与判定 |
| 提交信息、分支、推送或 PR | [jetlinks-delivery](../jetlinks-delivery/SKILL.md)：版本交付 |
| 维护稳定知识、规范或技能 | [jetlinks-capture](../jetlinks-capture/SKILL.md)：知识归属 |

只在当前动作确有需要时加入通用能力：

- 根因有竞争解释、共享契约未决或诊断反复失败：[systematic-solving](../systematic-solving/SKILL.md#admission)。
- 独立切片值得委派且宿主允许：[agent-orchestration](../agent-orchestration/SKILL.md#admission)。
- 已有任务需要保存、恢复或交接：[task-continuity](../task-continuity/SKILL.md)。普通新任务不先做恢复审计。

已明确的目标、约束和授权持续有效。选中入口后直接推进；只在实际边界改变时补规则，不为新一轮对话重读全部技能。

## 按需扩展

- 后端行为变化：[设计与验证](references/backend-design-test-driven-rules.md)。这是共享规则文件，直接使用它不要求先执行 router。
- JetLinks 特有代码关系：[导航扩展](references/code-navigation-jetlinks-rules.md)；复杂诊断中的领域映射：[求解扩展](references/systematic-solving-jetlinks-rules.md)。
- 内容落点：[制品归属](references/document-placement-rules.md)；实际 Git / Trellis 恢复：[恢复映射](references/context-recovery-rules.md)；已采用 Trellis 的项目接入：[集成规则](references/trellis-integration-rules.md)。
- 路由仍不明确：[组合示例](references/ai-prompt.md)；维护路由行为：[评测用例](references/evaluation-cases.md) 与 [评测器](scripts/evaluate_route_trace.py)。

按条件读取相关章节即可。路由结论通常一句话；评测字段不作为普通任务的报告模板。
