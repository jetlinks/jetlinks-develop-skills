# 后端设计与验证规则

组织变化契约与有效证据，不是新增审批流程。可由领域技能直接引用；无需先加载 router，也不要求每项改动另写设计文档。

## 触发条件

新增或改变后端的可观察结果、持久化、权限、状态、消息、报文或公开契约时，明确受影响目标及验收。只调整文案、导入、注释或沿已明确契约贯通实现时，直接采用已有事实与相称验证。

跨层、技术关键词或新接口本身不触发复杂求解。只有存在竞争根因或重大未决契约时使用 [systematic-solving](../../systematic-solving/SKILL.md#admission)。

## 契约与授权

保留本次决定所需的目标、范围、关键语义 / 取舍与验收；用户请求、已接受设计和现有代码契约均可作为来源，不为无关类别填表。

若公共设计、资源策略或跨边界行为仅由一个样例 / 未验证建议支撑，按 [扩大依据](../../systematic-solving/references/systematic-solving-rules.md#扩大依据的时机) 核对相关规范与成熟实践；查证服务当前决定，不增加全套求解或审批流程。

已有目标、约束与实施授权持续有效。先用代码和文档解决事实问题，仅在以下情况询问：

- 多种语义仍会改变用户结果、权限、持久化或外部契约，且现有证据 / 指令无法选择。
- 确需超出范围、增加权限，或适用的项目规则要求尚未取得的审批。

先完成已授权的独立工作，提供可审查结果与具体分歧；不把沉默当授权，也不为实现步骤变化重新审批。

## 专项规则归属

按真实变化选择，不必读取整表：

| 改变的内容 | owner |
| --- | --- |
| 模块落点 / 公开实现边界 | [routing](../../jetlinks-routing/SKILL.md) / [boundary](../../jetlinks-boundary/SKILL.md) |
| 状态、校验、数据查询 / 批量与 SQL | [CRUD](../../jetlinks-crud/SKILL.md) |
| 数据权限与独立安全入口 | [AssetsHolder](../../jetlinks-assets-permission/SKILL.md) |
| 事务连接、并发、取消与背压 | [reactive](../../jetlinks-reactive/SKILL.md) |
| 消息时机、幂等与可靠交付 | [events](../../jetlinks-events/SKILL.md) |
| 公共契约与非显然注释 | [代码注释](../../jetlinks-conventions/references/code-comments.md) |
| 关键业务追踪 / 常驻资源运维 | [TraceHolder](../../jetlinks-conventions/references/tracing.md) / [MBean](../../jetlinks-conventions/references/mbean-observability.md) |

已有平台观测覆盖时复用；不强制新增 span / MBean，也不为未改项写“不适用”证明。资源语义与通用组件修复分别使用 conventions 的 [运行状态](../../jetlinks-conventions/references/runtime-state-rules.md) 和 [根因处理](../../jetlinks-conventions/references/root-cause-and-no-hack-rules.md)。

## 发布边界与兼容性判断

- 先核验已发布、主线调用、持久化数据、配置 / 消息或外部消费者是否依赖旧行为；确有依赖时设计必要迁移、适配和退出条件。
- 同 PR 未发布的早期字段、接口、测试或别名直接收敛为单一实现，同步调用方与文档，不为中间形态保留双协议。
- 证据不足时先查发布与调用事实；仅当剩余不确定会改变方案时询问，不为“保险”增加兼容分支。

## 测试目标与真实性

从实际变化选择可观察断言，而不是先填测试类型清单：

- 新能力的真实主路径；bug 的原始触发；共享行为改变时的同类代表。
- 只有语义变化时补输入 / 异常、状态、幂等、部分失败和权限 allow / deny；不为异常测试发明生产 guard。
- 集成 / 端到端仅用于低层证据观察不到的契约、装配、序列化、持久化或跨边界传播风险。
- 性能证据仅针对变化的查询形态、规模、索引、分页、并发或批量风险，选择计划、压力或相称替代检查。
- 仓库已有覆盖率门槛继续遵守；无门槛不凑数字、不为可逆小改动制造镜像测试。

输入校验、权限和持久化不变量分别由其 owner 保证，不因测试需要复制检查。测试数据遵守真实约束；不得关闭有效断言、只 mock 争议核心、吞异步错误、随机 sleep 或将错误输出改成预期。陈旧测试和无效 fixture 在其 owner 修复，不以“保持测试”为由保留错误契约。

## 阶段验证与文档

先映射已有证据，只补真实缺口；连贯阶段结束集中验证，不逐操作构建。源码与相关测试、配置、依赖、环境、验收仍匹配时复用结果，commit hash 改变不单独使其失效。交付细则见 [delivery](../../jetlinks-delivery/SKILL.md)。

共享契约、跨边界权限 / 状态 / 持久化 / 生命周期或跨仓接入实质变化时，集成收尾按 [任务整体审查](../../jetlinks-review/references/review-method.md#任务整体审查) 核对累计结果与消费者。文件多或新增接口本身不触发全套流程，也不增加审批。

需要选择载体时查 [制品归属](document-placement-rules.md)；已有授权范围内原位更新改变的长期契约，不创建运行态文档作为开工条件。计划、失败与 Next 留任务运行态，测试证据留 PR / CI，权威 docs 不追加阶段总结。
