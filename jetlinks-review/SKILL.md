---
name: jetlinks-review
description: 按业务行为与完整生命周期审查 JetLinks 代码、PR 或方案。适用于对象建模、查询与写入、状态流转、跨服务联动、事件订阅、规则任务、缓存资源、前端交互及版本演进的正确性、安全性、复杂度和平台契约审查；从真实代码与评审案例取证，引用对应开发技能。
---

# JetLinks Review

从用户要完成的业务及其结果出发，审查实际行为、职责和契约。问题不限于已列举的坏味道：先看是否做对事情、是否安全和可恢复，再看复杂度与平台一致性。开发规则由对应领域技能拥有；本技能负责审查路径、证据和判定。

## Workflow

1. 确认审查对象、基线、目标版本和范围。PR 对比 base，工作树区分已提交与未提交变化；方案审查只能评价已给出的设计。用户要求整体审查时，沿入口、契约、状态和副作用扩展到相关模块，不止读 diff，也不默认扫描整个仓库。
2. 从变化的业务行为选审查切片，沿入口 → 业务决策 / 状态 → 持久化 / 外部能力 → 返回 / 后续消费者追完整路径；任务、回调、订阅与命令同样是入口。按本次变化检查权限、数据语义、失败 / 重放、并发、资源和版本边界。没有落在表格中的场景也按这条路径分析，不以未列举为由跳过。
3. 用 [证据与判定方法](references/review-method.md) 区分真实缺陷、维护问题、待核实疑点和个人偏好。提出问题前检查合理反例；没有证据时继续定点取证或说明不确定性，不将关键词命中当结论。
4. 按影响排序，给出触发条件、准确代码位置、实际后果和共同根因层的修复方向。纯审查不默认修改代码；用户已授权修复时，回到规则 owner 实现最小完整变化。
5. 在连贯阶段结束后集中验证。规则 / 文档检查不能证明业务正确；历史会话中的测试结果不能作为当前分支已验证的证据。未执行必要运行检查时说明覆盖缺口。

## 按业务场景选择审查切片

| 当前业务行为 | 关键判断与开发规则 |
| --- | --- |
| 建对象、加字段、拆模块、提供扩展能力 | 身份 / 关系 / 生命周期、契约 owner 与实现依赖；[职责与语义](../jetlinks-conventions/references/responsibility-and-generality-rules.md)、[平台依赖与版本化字段扩展](../jetlinks-boundary/references/application-platform-rules.md) |
| 列表、搜索、树、关联、统计与历史查询 | 条件 / 权限是否在分页前生效，count / 行 / 汇总语义、空与零、规模和 N+1；[高级查询](../jetlinks-crud/references/advanced-crud-rules.md)、[数据权限](../jetlinks-assets-permission/SKILL.md) |
| 新增、修改、删除、导入、导出与批量处理 | PATCH / 完整替换、级联与事务、部分成功、重放与数据边界；[CRUD](../jetlinks-crud/SKILL.md)、[批量与文件](../jetlinks-crud/references/advanced-crud-rules.md#导入导出与批量失败) |
| 审批、工单、支付、认领、发布 / 撤销等状态流转 | 合法前态、并发仲裁、重复请求、迟到结果与业务回执；[状态与重复请求](../jetlinks-crud/references/common-crud-rules.md#状态流转与重复请求) |
| 命令、远端查询 / 动作、第三方回调或工具调用 | 信任边界、Context、路由、业务空结果、超时后的未知结果与重试；[跨服务调用](../jetlinks-boundary/references/cross-service-call-rules.md)、[授权](../jetlinks-assets-permission/SKILL.md) |
| 保存后联动、可靠消息、通知与异步投递 | 本地原子性、提交时机、持久受理 / 执行成功、失败恢复与幂等；[事件规则](../jetlinks-events/references/event-driven-rules.md) |
| 实时订阅、告警、历史加实时、断线重连 | Topic / 权限与查询一致，交接、乱序、重放、背压和取消释放；[订阅规则](../jetlinks-events/references/realtime-subscription-rules.md)、[响应式实践](../jetlinks-reactive/SKILL.md) |
| 规则 / 指标编译、流程运行、调度和配置启停 | 定义 / 版本 / 运行实例关系、热路径成本、执行身份、停用与重配置；[事件与运行生命周期](../jetlinks-events/SKILL.md)、[运行状态](../jetlinks-conventions/references/runtime-state-rules.md) |
| 缓存、会话、连接、队列、文件与后台任务 | 权威数据源、key / 版本、所有权、容量、释放和恢复；[运行状态](../jetlinks-conventions/references/runtime-state-rules.md)、[资源与并发](../jetlinks-reactive/references/reactive-practice.md) |
| DTO / 元数据 / 序列化、协议、配置和插件装配 | 类型、单位、精度、缺失 / null、可移植性、适用版本与扩展能力；[数据契约](../jetlinks-conventions/references/responsibility-and-generality-rules.md#数据契约与配置)、[协议](../jetlinks-protocol/SKILL.md)、[平台边界](../jetlinks-boundary/SKILL.md) |
| 前端列表 / 详情、编辑、配置与持续操作 | 任务是否闭环、状态 owner、草稿与保存、旧响应覆盖、组件契约和可访问性；[web](../jetlinks-web/SKILL.md) 的相关规则 |
| 安装、升级、迁移、历史 / 审计、兼容与交付 | 用户数据、初始化归属、留痕用途、已发布契约及有效证据；[通用性](../jetlinks-conventions/references/responsibility-and-generality-rules.md)、[运行留痕](../jetlinks-conventions/references/runtime-state-rules.md#历史审计与可观测性)、[交付](../jetlinks-delivery/SKILL.md) |

具体怎么沿代码判定见 [场景链路与反例](references/scenario-review-map.md)。职责、依赖、过度校验、魔法值、特调和操作符堆积是贯穿这些场景的观察角度，不是审查范围的上限。只展开实际变化及其相关风险，不将上表变成每次必填清单。

规则依据及跨仓库历史评审见 [资料与适用边界](references/design-sources.md)；维护技能时用 [正反场景](references/evaluation-cases.md) 走查。不要求普通审查先读完全部技能。

## 输出

- 优先报告可行动发现，按仓库已有严重性约定排序；每项包含位置、触发、影响与修复方向，同一根因不拆成多条凑数量。
- 行为 / 安全缺陷与可维护性改进分别说明；后者应解释职责泄漏、修改扩散、重复 I/O 或语义歧义的具体成本，不假装已有线上故障。
- 没有实质问题时直接说明，并交代真实审查范围和未验证边界。规则引用、检查项数量、文件行数或命名偏好都不能单独证明有缺陷。
- 不因“整体审查”增加无关构建、重写或发布动作。提交与 PR 仅在用户授权后交给 [delivery](../jetlinks-delivery/SKILL.md)。
