---
name: jetlinks-router
description: 为尚未确定入口或当前边界发生变化的 JetLinks 开发任务选择最少的相关技能。覆盖模块定位、协议、CRUD、权限、事件、响应式、前端、编码规范及交付；恢复、复杂求解和多智能体协作分别交给对应通用技能。
---

# JetLinks Router

本技能只选择入口。任务已经选中正确的 focused skill 时直接继续；不因进入新一轮对话重新走完整路由。

## Workflow

1. 先区分实际恢复与新请求。压缩、暂停续作或交接时，交给 [task-continuity](../task-continuity/SKILL.md) 核对主目标、持续约束、当前状态和保存的下一动作；匹配后复用原路线。新任务中的精确 symbol / changed path 直接交给 code-navigation。
2. 对新任务或真实路线失配，确定当前要回答的判断或执行的动作，选择下表中能直接承担它的最少技能。领域名出现在背景中不构成加载理由。
3. 只补充当前动作涉及的领域规则。确有复杂求解需求时，准入统一由 [systematic-solving 的 Admission](../systematic-solving/SKILL.md#admission) 判定；编排选择、派发和验收交给 agent-orchestration；不在 router 重新定义这些流程。
4. 用户已明确目标、约束并要求实施时直接推进。多轮中的补充约束、进度提问或提醒仍服务原任务；只有明确取消、替换目标或实质未决决策才改变主线。授权与计划是否需要补充，按相关规则的适用范围判断。
5. 在当前边界的连贯阶段完成后验证；引用仍有效的证据，只补缺口。交付、知识沉淀仅在请求或真实需求出现时加入。

路由结果通常一句话即可说明“当前判断 → 所选技能 → 下一动作”。只有路由评测或宿主需要机器记录时，使用 [路由评测约定](references/evaluation-cases.md) 的 `current_decision`、`minimum_skills`、`user_confirmation_required`、`unique_next`；普通任务不必填表。

## Routing

| 当前动作 / 判断 | 入口 |
| --- | --- |
| 精确符号、调用关系、依赖、影响范围 | [code-navigation](../code-navigation/SKILL.md) |
| 工作区结构、模块归属或新模块 | [jetlinks-routing](../jetlinks-routing/SKILL.md) |
| 协议注册、传输编解码、二进制报文、认证与应答关联 | [jetlinks-protocol](../jetlinks-protocol/SKILL.md) |
| Entity / Service / Controller、查询与批处理 | [jetlinks-crud](../jetlinks-crud/SKILL.md) |
| AssetsHolder 数据权限、关联资产、独立暴露边界 | [jetlinks-assets-permission](../jetlinks-assets-permission/SKILL.md) |
| 直接依赖、Command / Provider / Proxy 边界 | [jetlinks-boundary](../jetlinks-boundary/SKILL.md) |
| 生命周期事件、领域事件、Topic / 订阅 | [jetlinks-events](../jetlinks-events/SKILL.md) |
| Mono / Flux、非阻塞与异步生命周期 | [jetlinks-reactive](../jetlinks-reactive/SKILL.md) |
| 命名、导入、注释、i18n、TraceHolder、MBean、扩展方式 | [jetlinks-conventions](../jetlinks-conventions/SKILL.md) |
| Vue 页面、交互、组件复用、前端状态与质量 | [jetlinks-web](../jetlinks-web/SKILL.md) |
| 分支、提交、验证证据或 PR | [jetlinks-delivery](../jetlinks-delivery/SKILL.md) |
| 跨任务稳定知识的维护 | [jetlinks-capture](../jetlinks-capture/SKILL.md) |
| 候选根因难区分、契约未决或反复失败 | [systematic-solving](../systematic-solving/SKILL.md) |
| 有独立切片且真实委派有收益 | [agent-orchestration](../agent-orchestration/SKILL.md) |
| 长任务主线、压缩恢复、交接、证据生命周期 | [task-continuity](../task-continuity/SKILL.md) |

## Conditional References

- 需要 JetLinks 特有的代码关系时：[代码导航扩展](references/code-navigation-jetlinks-rules.md)。
- 已进入复杂求解且需要领域映射时：[系统性求解扩展](references/systematic-solving-jetlinks-rules.md)。
- 后端新增能力或行为变化需要设计 / 验证组织时：[后端设计与测试规则](references/backend-design-test-driven-rules.md)；此流程复用用户已有授权，不自动追加确认。
- 需要选择文档或运行态落点时：[制品归属](references/document-placement-rules.md)；使用 Git / Trellis 的恢复适配时：[恢复映射](references/context-recovery-rules.md)；检测到 Trellis 且需要其流程时：[Trellis 集成](references/trellis-integration-rules.md)。
- 需要更细的场景组合示例时：[路由索引](references/ai-prompt.md)；维护路由行为时：[评测用例](references/evaluation-cases.md) 与 [离线评测器](scripts/evaluate_route_trace.py)。

局部事实以当前工作区代码、导出、构建声明和有效锚点为准；不猜固定模块名，不忽略软链接模块。以上 references 按需读取，不是每次任务的前置阅读清单。
