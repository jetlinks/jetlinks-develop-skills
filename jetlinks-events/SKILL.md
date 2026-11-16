---
name: jetlinks-events
description: 实现 JetLinks 生命周期事件、领域联动、可靠投递和 Topic 订阅。区分本地事务不变量、外部副作用与持续消息流。
---

# JetLinks Events

负责何时触发、交付承诺及消息生命周期；不替代 CRUD 的状态事务、boundary 的命令契约或 reactive 的执行机制。

## 工作方式

1. 识别一次性查询 / 命令、必须原子完成的本地联动、外部通知或持续流，不能仅因“保存后”就默认异步化。
2. 生命周期 / 领域联动读 [事件规则](references/event-driven-rules.md)；Topic、EventBus、历史加实时或重连读 [订阅规则](references/realtime-subscription-rules.md)。
3. 核实真实发布时机、是否等待处理、Context 和失败传播；“修改后”不等于“事务提交后”。
4. 新增或改变后端行为时，按 [设计与验证](../jetlinks-router/references/backend-design-test-driven-rules.md) 验证改变的触发与交付语义。

## 关键约束

- 本地关系清理、状态等必须一致的不变量留在所属事务；外部副作用在安全提交边界交付。
- 提交后回调不保证可靠送达。确有可靠性需求时复用平台持久待办 / 投递 / 消费幂等，不为每个通知创建 outbox。
- 受理、持久受理、执行完成、消费者处理是不同成功阶段；ACK、重试、重放和恢复遵守实际契约。
- 消息身份、顺序、循环触发、部分失败及批量边界按业务处理；不能只用时间窗丢弃“看似重复”的合法事件。
- 持续订阅保持权限 / Topic 与查询一致，处理历史实时交接、背压、取消、重连与旧资源释放；一次性查询不伪装订阅。
- 配置保存、发布、生效和运行实例版本分开，停用 / 重配 / 删除时处理旧资源与迟到结果，参见 [运行状态](../jetlinks-conventions/references/runtime-state-rules.md)。

说明实际时机、交付承诺与恢复 owner；只验证本次改变的行为，非显然边界在代码旁简注。
