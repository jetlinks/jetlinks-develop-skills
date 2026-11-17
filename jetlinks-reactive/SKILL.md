---
name: jetlinks-reactive
description: 处理 JetLinks Mono / Flux 的订阅语义、非阻塞边界、事务串行、有界并发与背压。纯同步计算无需响应式包装。
---

# JetLinks Reactive

负责执行、需求信号与异步资源机制；业务状态归 CRUD，事件投递语义归 events，资源的业务归属归 conventions。

## 工作方式

1. 核实当前模块是响应式还是阻塞式，不为风格统一转换编程模型。
2. 沿真实 Publisher / 异步 I/O 找到订阅、事务 / 连接、取消和资源 owner，按 [响应式实践](references/reactive-practice.md) 读取相关章节。
3. 新增或改变后端行为时，按 [设计与验证](../jetlinks-router/references/backend-design-test-driven-rules.md) 验证受影响信号和业务结果。

## 关键约束

- 响应式业务链不 `block()`、嵌套 `subscribe()`、`Future.get()` 或 sleep 等待。不可避免的阻塞 I/O 在明确适配边界用项目认可的 scheduler 隔离；包装成 Mono 不等于非阻塞。
- 保留 demand、取消、终止、Context 与订阅期语义；不能用全局可变状态或 ThreadLocal 替代 Context。
- 纯转换、计算和谓词用普通函数，移除无意义 `just().map()`、identity map、`flatMap(Mono::just)` 等包装；真实需要的 `defer / fromSupplier` 不属于冗余。
- 操作符表达语义步骤，多阶段流程抽成命名方法；不用操作符数量或链长单独判错。
- 同事务共享连接的数据库操作串行，必要时先消费完外层结果；`flatMapSequential` 只保证输出顺序，不串行执行。详见 [事务与并发](references/reactive-practice.md#事务与数据库并发)。
- 事务外并发读先排除 N+1，按独立性、顺序与资源预算选择 concurrency、prefetch、批次；不复制固定大数，也不把所有流强制串行。
- `collectList()` 必须有真实规模边界；持续流按背压和取消释放处理，重试 / 超时不掩盖部分副作用。
- 用信号、确定性同步及必要的实际连接验证结果、顺序、失败与清理，不靠随机 sleep、吞错或弱化断言过测。

只报告本次链路决策与证据；追踪、公共契约注释等分别使用 [conventions](../jetlinks-conventions/SKILL.md) 的对应细则。
