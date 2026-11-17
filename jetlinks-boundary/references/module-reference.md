# JetLinks 边界方式选择

负责选择交互方式。应用依赖平台及标准字段扩展先遵守 [平台规则](application-platform-rules.md)，相邻旧实现不能放宽该边界。

| 需要的语义 | 方式与边界 |
| --- | --- |
| 同一业务边界内的本地复用 | 公开接口 / SPI，依赖必须合法，不注入其他边界内部实现 |
| 跨服务查询或业务动作 | 平台命令；核验提供方、路由、Context、载荷及结果契约 |
| 已完成动作的领域事实或外部联动 | 事件；时机、等待与可靠性由 events 决定 |
| 持续消息、广播或实时消费 | 订阅；明确 Topic、权限、背压与生命周期 |

先查实际公开契约、构建依赖和相邻 provider / consumer，再选最小耦合方式，不臆造 service / command / support ID 或 Topic。

本地关系清理、状态等必须原子一致的操作留在业务事务内；“保存后”或“调用方不取返回值”不等于可以异步化。副作用方式按 [事件规则](../../jetlinks-events/references/event-driven-rules.md) 判断。

空模板不为“以后拆服务”创建命令框架，但缺少样例也不能成为应用直接依赖平台 manager 或绕开跨服务命令的理由。先核验目标版本与依赖；只有真实缺能力才处理 [正式扩展 / 修复](../../jetlinks-conventions/references/root-cause-and-no-hack-rules.md)。

实现命令读 [调用规则](cross-service-call-rules.md)；已有显式命令类时使用命令对象与 `commandSupport.execute(...)`，不退化为匿名 payload。报告实际边界选择与必要理由，不填固定输出表。
