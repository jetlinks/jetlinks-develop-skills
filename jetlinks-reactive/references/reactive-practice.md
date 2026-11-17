# JetLinks 响应式编程实践

本文件用于在 JetLinks 系项目中处理响应式实现细节，避免把“用了 `Mono` / `Flux`”误当成“已经是正确的响应式实现”。

## 第一原则：先确认当前模块是不是响应式

- 看控制器返回类型
- 看服务基类和仓储抽象
- 看相邻模块是否普遍使用 `Mono`、`Flux`、异步事件或异步订阅

如果当前模块是阻塞式：

- 不要为了局部新功能强行包一层响应式外壳
- 跟随现有阻塞式事务边界和调用模式

## 响应式模块的基本要求

1. 保持链路连续
   - Controller、Service、事件处理器、订阅处理器之间保持 `Mono` / `Flux` 传递。
   - 不在中间用 `block()` 回退成同步流程。

2. 不用 `subscribe()` 驱动主业务
   - 主业务控制流应留在返回链中。
   - `subscribe()` 只能用于框架托管之外、且已明确隔离的边缘场景。

3. 批处理优先于逐条处理
   - 批量更新、批量删除、消息消费、联动同步优先使用批量抽象。
   - 避免在 `flatMap` 里逐条做数据库或远程调用，形成 N 次往返。

4. 副作用按业务与事务契约组合
   - 必须参与当前用例结果的操作留在返回链；本地不变量与外部交付按 [事件规则](../../jetlinks-events/references/event-driven-rules.md) 选择时机。
   - 不因逻辑复杂就异步化，也不假设放进本地事务的远程调用可以回滚。

## 官方定义与工程边界

参考官方定义：

- Reactive Streams 定义的是异步流处理与非阻塞背压协议，核心角色是 `Publisher`、`Subscriber`、`Subscription`、`Processor`。
- `Publisher` 只能在订阅后按 `Subscription.request(n)` 需求发送数据；`onError` / `onComplete` 是终止信号；`cancel` 表示下游不再需要数据。
- Reactor 的 `Mono` / `Flux` 是 `Publisher` 实现；操作符本质上是把一个 `Publisher` 组合成另一个 `Publisher` 的函数描述，实际执行发生在订阅后。
- `publishOn` / `subscribeOn` 是显式线程调度边界；`boundedElastic` 只用于无法避免的遗留阻塞调用隔离，不作为普通异步化手段。

官方来源：[Reactive Streams JVM](https://github.com/reactive-streams/reactive-streams-jvm)、[Reactor Reference Guide](https://docs.spring.io/projectreactor/reactor-core/docs/current/reference/html/)。

落到 JetLinks 代码里：

- 响应式链路从已有 `Publisher` 或第一个真实异步边界开始：响应式仓储、远程命令、事件发布、消息订阅、异步缓存等。
- 当前调用栈上的普通对象不是响应式边界。请求对象校验、DTO 转换、字段计算、条件判断先用普通函数完成。
- 每个操作符都要能说清语义：转换、筛选、异步调用、顺序组合、并发组合、错误恢复、忽略前值后的下一步、资源或背压控制。
- lambda 中混入难以追踪的多个业务阶段时，用命名函数表达边界；直观的局部步骤可留在原处，不把过程式写法本身当缺陷。

## 常见设计准则

### 选择映射算子

- 需要保持顺序时，优先 `concatMap`
- 需要并发且独立性、顺序与资源预算允许时，使用 `flatMap`；相邻惯例不能代替这些依据
- 只做同步映射时，使用 `map`
- `flatMap` 用于组合返回 Publisher 的步骤；它本身不创建线程或保证异步，不为纯转换额外包装 Publisher
- 对象转换、字段计算、条件判断等没有异步边界的函数保持普通返回值，不额外封装成 `Mono` / `Flux`
- `flatMapSequential` 会并发订阅后按序发出结果，不能把它当串行数据库执行；真正串行选择 `concatMap`，并继续核对上游是否持有未消费的数据库游标。

### 保持算子简洁

- 不写无意义链路：`Mono.just(x).map(f)` 优先改为先计算再 `Mono.just(result)`；需要懒执行或异常进入链路时才用 `Mono.fromSupplier` / `Mono.defer`
- 当前栈上已有普通对象时，不用 `Mono.just(request).map(...).flatMap(...)` 开链；先用普通函数构造参数，再直接调用第一个响应式边界，例如 `repository.save(request.toEntity())`
- 不写 `.flatMap(Mono::just)`、`map(v -> v)`、`then(Mono.just(x))` 这类可读性更差的中转；优先 `map`、直接返回、或 `thenReturn(x)`
- 相邻 `.map(...).map(...)` 如果属于同一个同步业务步骤，合成一个按业务意图命名的普通函数；不要把校验、状态整理、字段赋值拆成一串小 `map`
- 相邻 `.filter().filter(...)` 能合并就合并；条件复杂时抽成命名谓词，避免链路被细碎条件淹没
- 必须参与成败的业务副作用不要放在 `doOnNext` / `doOnSuccess` 里，使用 `flatMap` / `then` 接入主链路
- 纯同步转换方法可在链路里用 `map(this::toView)` / `filter(this::isVisible)`，不要改成 `Mono<View> toView(...)`
- 精简时保持执行时机：需要每次订阅重算、把异常送入错误信号、读取 Reactor Context 或等待前一步后才构造副作用时，保留必要的 `defer` / `deferContextual` / `fromSupplier`。不能把订阅期业务提前到组装期，或把每次订阅创建的可变对象变成共享对象；纯函数本身仍用普通返回值。

### 事务与数据库并发

- 先定位事务框架、传播范围、连接 / 会话获取与归还，以及流式结果消费时机。同一 reactive Context 中的多条链可能共享同一个事务连接，不能从 `Mono.zip` 的外形推断资源彼此独立。
- **同一事务共享连接 / 会话上的数据库操作禁止并发发起**，读取也适用。不要用 `zip`、`when`、`merge`、并发 `flatMap`、`parallel` 或 `flatMapSequential` 同时执行；优先集合 SQL / 批量接口，其次 `then`、`concatMap` 等串行组合，并等待真实完成。
- 串行子操作仍要检查外层查询：一边流式读游标一边在同连接执行子查询 / 写入，可能仍有语句重叠。优先批量关联查询，或在合理分页 / 批次内完整消费结果后再处理；不能为此把无界流全部 `collectList()`。
- 不用换 scheduler、手动 `subscribe()`、另取连接、关闭事务或为每条数据新开事务“解决”并发冲突，这会改变原子性和上下文。同一业务确需独立事务时必须先明确独立提交与失败语义。
- 所有必须成功的持久化操作留在返回链中，错误 / 取消按实际事务框架回滚。外部命令、消息和缓存不因位于本地事务链就具备原子性；按既有提交后事件、可靠消息或幂等契约处理，不吞掉事务内错误返回成功。
- `zip` 组合独立远程读取或事务外、资源互不共享的查询可以合理使用；禁止的是共享事务资源上的并发执行，不是所有组合算子。纯内存转换也不属于数据库操作。

### 事务外的有界并发读取

- 先判断能否用一次批量 / 集合查询，避免给 N+1 查询加并发掩盖多次往返。允许并发前确认读操作独立、可乱序且不共享事务连接；有顺序依赖时串行。
- Reactor `flatMap(mapper, concurrency, prefetch)` 的 `concurrency` 限制同时订阅的内部 Publisher 数，`prefetch` 控制每个内部流的请求窗口，二者都不等于连接池大小或数据库请求吞吐；具体行为以目标 Reactor 版本为准。
- 并发读上限结合可用连接预算、并发请求数、嵌套 fan-out、下游限额、单项成本和等待时间确定。每个请求都开到池大小、无界并发、复制固定大数字或为“提速”提升上限，都需要纠正其资源模型。
- 批量大小、并发数和预取量是不同维度。不要把同一个数字到处复用，也不要把所有 `flatMap` 强制改成 `concatMap`；低成本有界流沿用库默认值可以合理，未显式写并发参数本身不构成问题。
- 规模 / 并发风险变化时，在阶段末验证受影响的排队、顺序、资源占用、错误 / 取消和事务行为；既有证据覆盖的直接复用，不为每处算子建立压测项目。

### 控制集合边界

- `collectList()` 只用于明确有界的数据：分页结果、固定批次、协议天然小集合、已校验大小的入参
- 订阅流、消息流、全表查询、设备属性历史、用户可控查询等可能很大的数据，不直接 `collectList()`
- 需要聚合时优先分页、`take` / limit、定长 `buffer` / `window`、批量仓储接口、`QueryHelper.transformPageResult`、`QueryHelper.combineOneToMany` 等既有组合方式
- 规模不明时先核对分页、来源和资源契约；只有剩余选择会改变业务结果时询问，不为每处收集新建设计稿。

### 控制 lambda 复杂度

- lambda 只承载局部转换、参数拼装或链路衔接
- 出现校验、查询、状态变更、副作用混在一起，或有嵌套分支、循环、`try/catch`、多次 DB / 远程调用时，抽成按业务意图命名的方法
- 抽出的私有方法按真实边界选择返回值：纯转换返回普通对象，包含 DB / 远程 / 异步副作用时才返回 `Mono` / `Flux`

### 控制链路长度

- 多阶段链路难以追踪时按业务意图提取完整步骤；直观的局部组合可以保留，不为缩短链长增加转发方法。
- 当链路同时包含已由业务契约要求且由当前边界拥有的校验、权限、命令发送、持久化、日志、事件或结果转换时，按真实业务阶段拆成命名步骤，例如 `checkTransitionAndSend(...)`、`saveXxxAndReturn(...)`、`publishXxxEvent(...)`。不要因方法名模板主动新增 `validateAndXxx(...)` 或重复上游 / 框架 guard。
- 嵌套造成阶段、副作用或错误边界难以追踪时拆分；动作数量不单独决定是否抽方法。
- 拆出的响应式方法仍返回 `Mono` / `Flux`，让超时、重试、错误传播和测试仍能组合。

### 链路追踪

- 关键响应式业务阶段使用 `MonoTracer.create(...)` / `FluxTracer.create(...)` 或当前模块已有领域 tracer，不用 `doOnNext` / `doOnSuccess` 伪装成埋点。
- span 放在真实异步边界或关键业务阶段上，例如命令发送、状态流转、事件发布、批处理、外部调用、协议解析。
- trace context 跨 HTTP、RSocket、消息、事件、RuleData 等边界时，使用 `TraceHolder.readToContext(...)` / `TraceHolder.writeContextTo(...)`，不要用 `ThreadLocal` 自己传递。
- span 名称和属性、敏感信息、批量粒度等规则见 [`../../jetlinks-conventions/references/tracing.md`](../../jetlinks-conventions/references/tracing.md)。

### 函数式组合示例

已有普通对象时，直接调用第一个响应式边界：

```java
// Bad
return Mono.just(request)
    .map(CreateRequest::toEntity)
    .flatMap(repository::save);

// Good
return repository.save(request.toEntity());
```

链路中的纯转换用命名函数：

```java
// Bad
return repository.findById(id)
    .flatMap(entity -> Mono.just(toView(entity)));

// Good
return repository.findById(id)
    .map(this::toView);
```

链路中先做纯转换，再组合已有持久化能力；空结果与事件时机沿当前用例契约，不由示例新增：

```java
return repository.findById(id)
    .map(entity -> applyUpdate(entity, request))
    .flatMap(repository::save);
```

只有片段确实复用或形成独立业务阶段时才提取组合函数；授权、状态校验和日志不因示例名称而被额外加入。追踪 API 示例由 [埋点规则](../../jetlinks-conventions/references/tracing.md#api-选择) 维护。

### 错误传播

- 对用户可见异常，优先在 `Mono.error(...)` / `Flux.error(...)` 中传递带 `i18nCode` 的异常实例。
- 不要在响应式链里直接 `Mono.error(new XxxException("对象不存在"))`。
- 只有当前模块的异常模型只支持 `message` 时，才在链路边界解析本地化文案。

### 阻塞依赖的处理

- 先找当前仓库有没有同类边界的非阻塞抽象
- 如果没有，只在必要边界隔离阻塞调用
- 依据当前执行模型和目标版本选择项目认可的阻塞适配边界；没有相邻样例不阻止必要隔离，换线程也不改变事务或资源所有权。
- 如果响应式链路里需要超时缓存，优先使用 `org.hswebframework.web.cache.ReactiveCache<E>`；需要本地 TTL / size 控制时，用 `com.github.benmanes.caffeine.cache.Caffeine<K, V>` 构建底层缓存，不要额外拼装临时缓存方案。

### 事件与订阅

- 事件处理器和订阅处理器优先返回 `Mono<Void>` 或当前框架惯用异步类型
- 高吞吐消息处理优先复用现有 `buffer`、`window`、批处理 sink、去重策略
- 处理器保持幂等，避免消息重放导致重复副作用

### 跨边界调用

- 调用其他模块或远程命令时，保持链式调用
- 不在响应式 consumer 里为了省事 `block`
- 参数组装尽量靠近边界，不把远程契约扩散到业务内部

### 注释边界

- 长链拆出的命名方法如果仍然承载非显而易见的异步边界、权限 / 命令 / 持久化顺序、重试 / 超时策略、取消语义、上下文传播或批量上限，需要在方法或关键分支前写短注释。
- `collectList()`、`buffer`、`window`、并发 `flatMap`、`take` / limit 等涉及数据边界或背压的地方，如果边界来自业务假设或协议限制，必须注释说明来源。
- TraceHolder / MonoTracer / FluxTracer 的 span 名称和属性选择如果看起来保守或刻意缺少 payload，需要注释说明敏感信息和基数边界。
- 直接 `map(this::toView)`、`flatMap(repository::save)`、`thenReturn(result)` 等语义清晰的链路胶水不写注释。

## 测试目标

- 用 `StepVerifier` 或项目既有测试方式验证值、完成 / 错误信号、顺序、并发、超时、重试和副作用
- 高频或批量路径验证没有 N+1 查询、无界 `collectList()`、无限并发 `flatMap` 或靠 `sleep` 等待的测试
- 对真实使用场景准备数据量：分页查询按页面规模，批处理按批次规模，订阅 / 消息流按持续输入验证背压或批量策略

## 自检清单

- 当前模块到底是响应式还是阻塞式
- 是否出现了 `block()`、嵌套 `subscribe()`、逐条低效调用
- 是否存在无意义算子、重复过滤、过大的 lambda
- 是否存在难以一眼看懂的长链；是否已按业务阶段拆成命名方法
- 关键业务阶段是否有 TraceHolder / MonoTracer / FluxTracer 埋点判断
- 是否对 `collectList()` 给出了明确的数据边界
- 是否为非显而易见的异步边界、批量 / 背压限制、重试 / 超时、生命周期清理、上下文传播补了必要代码注释
- 必须等待的步骤是否仍在返回链，本地不变量与外部交付是否符合事件 / 事务契约
- 是否保持了链路返回类型与相邻代码一致
- 是否对高频或批量场景做了批处理而不是逐条处理
