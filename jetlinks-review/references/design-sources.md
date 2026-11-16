# 资料与适用边界

用于解释设计取舍和维护规则。资料支撑一般原理，平台公开契约与目标制品决定具体 API；应用禁止依赖平台实现、2.21 扩展策略等属于本项目明确约束，不能伪称为行业通用禁令。

| 资料 | 支撑的判断 | 不可机械推导的结论 |
| --- | --- | --- |
| Martin Fowler：[Bounded Context](https://martinfowler.com/bliki/BoundedContext.html) | 不同上下文有自己的模型与语言，应明确边界和相互关系 | 每张表一个服务、所有调用远程化、仅改包名就完成解耦 |
| Martin Fowler：[Replace Magic Literal](https://refactoring.com/catalog/replaceMagicLiteral.html) | 有业务含义的字面量用符号名称表达，便于理解与维护 | 所有数字抽常量、命名常量后数值策略自然合理 |
| OWASP：[Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) | 区分语法和语义校验，正确处理信任边界；标识合法不等于有权访问 | 每一层重新校验所有字段、前端校验可替代服务端授权 |
| [Reactive Streams JVM 规范](https://github.com/reactive-streams/reactive-streams-jvm) | 按需求发出、取消和终止信号；非阻塞背压属于协议契约 | 包成 Mono 就不阻塞、纯内存函数都要返回 Publisher |
| Reactor：[Flux Javadoc](https://docs.spring.io/projectreactor/reactor-core/docs/current/api/reactor/core/publisher/Flux.html) 的 `flatMap` / `flatMapSequential` / `concatMap` | 并发订阅、按序输出和串行执行不同；concurrency 与 prefetch 控制不同窗口 | 按序输出就没有并发、固定并发值适合所有池和负载 |
| Spring：[Programmatic Transaction Management](https://docs.spring.io/spring-framework/reference/data-access/transaction/programmatic.html) | TransactionalOperator 的事务范围与取消；Spring 5.3 起取消会触发回滚，多值结果需完整消费 | 任意事务框架都自动提供相同取消语义、本地事务覆盖远端命令 |
| Spring：[R2DBC](https://docs.spring.io/spring-framework/reference/data-access/r2dbc.html) 的 R2dbcTransactionManager | 事务连接绑定 subscriber Context，可由多条组合链共享 | 多个 Mono 意味着多个连接、切换线程后事务自动独立 |
| [R2DBC 1.0 规范](https://r2dbc.io/spec/1.0.0.RELEASE/spec/html/) §6 Connections / §7 Transactions | Connection 是带事务状态的会话；不保证多个订阅者并发修改状态安全 | 所有驱动行为完全相同、所有事务外读取都禁止并发 |

Reactor 的 current 文档会随版本变化，执行前以项目锁定版本核对；Spring R2DBC 用于解释资源共享，JetLinks 的实际事务实现、传播和取消仍须从当前框架确认。项目采用共享事务连接上串行数据库操作的开发约束，不能据此声称所有数据库驱动天生无法流水执行。

## 平台实现依据

声明式扩展核对过 `jetlinks-components` 的 `codex/entity-extension` 开发分支（提交 `5fee7da6bd077fa7130585879d752712c8ea376b`，并有后续在途修改）。[PR #1707](https://github.com/jetlinks-v2/jetlinks-components/pull/1707) 是能力追踪入口，不能替代目标版本已发布的证明。

- `common-component/.../rdb/extension/EnableEntityExtension.java`：主实体启用、target / 身份 / 候选配置；`EntityExtension.java`：共享主键一对一依附表声明。
- `TableExtensionSupport` / `EntityExtensionRuntime`：声明式组合、CRUD / 查询、元数据与本地事务协调；在线动态配置在 `entity-extension-component`。
- 具体开发约束只维护于 [应用与平台边界](../../jetlinks-boundary/references/application-platform-rules.md)，字段路径、版本分支和限制不在此重复定义。

## 最近审查会话提炼出的通用反例

- 解析算法引用上层选窗类型形成反向依赖；实验适配的可变请求体逻辑污染通用生产接口。规则落在 [职责与通用性](../../jetlinks-conventions/references/responsibility-and-generality-rules.md)。
- 保存命令与通用保存重复绑定资产；授权撤销被未变化的历史规则阻止，但删除精确规则也可能激活更宽 fallback。规则落在 [校验与变化语义](../../jetlinks-crud/references/common-crud-rules.md#校验范围与变化语义)。
- 内部 find 的合法 empty 与 RPC 执行缺少命令的错误需要区分；不能全局把 empty 变异常，也不能用额外 exists RPC 重复预检。按目标版本真实命令契约处理。
- 业务 Provider 接入统一关系后仍须核验新分页签名、授权和模型；接口存在不等于集成完成，业务事实也不应双写通用关系表。

这些是案例提炼，不固定问题数量、类名或历史修复状态。旧会话的测试计数不证明任何新审查或实现已通过。
