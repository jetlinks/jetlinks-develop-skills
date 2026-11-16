# 资料与适用边界

用于解释设计取舍和维护规则。资料支撑一般原理，平台公开契约与目标制品决定具体 API；应用禁止依赖平台实现、2.21 扩展策略等属于本项目明确约束，不能伪称为行业通用禁令。

| 资料 | 支撑的判断 | 不可机械推导的结论 |
| --- | --- | --- |
| Martin Fowler：[Bounded Context](https://martinfowler.com/bliki/BoundedContext.html) | 不同上下文有自己的模型与语言，应明确边界和相互关系 | 每张表一个服务、所有调用远程化、仅改包名就完成解耦 |
| Martin Fowler：[Replace Magic Literal](https://refactoring.com/catalog/replaceMagicLiteral.html) | 有业务含义的字面量用符号名称表达，便于理解与维护 | 所有数字抽常量、命名常量后数值策略自然合理 |
| OWASP：[Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) | 区分语法和语义校验，正确处理信任边界；标识合法不等于有权访问 | 每一层重新校验所有字段、前端校验可替代服务端授权 |
| AWS Builders' Library：[Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | 请求身份、重复请求和不同意图需要明确语义；超时后重试必须考虑副作用已执行 | 给所有查询增加回执表、用对象 ID 去重全部后续动作、同键不同载荷静默成功 |
| Microservices.io：[Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html) | 本地写入和外部消息之间存在可靠性交接；relay 也可能重复发送，消费者仍需相应幂等 | 所有事件都必须增加 outbox、提交后回调就等于可靠交付、自动获得全局 exactly-once |
| [Reactive Streams JVM 规范](https://github.com/reactive-streams/reactive-streams-jvm) | 按需求发出、取消和终止信号；非阻塞背压属于协议契约 | 包成 Mono 就不阻塞、纯内存函数都要返回 Publisher |
| Reactor：[Flux Javadoc](https://docs.spring.io/projectreactor/reactor-core/docs/current/api/reactor/core/publisher/Flux.html) 的 `flatMap` / `flatMapSequential` / `concatMap` | 并发订阅、按序输出和串行执行不同；concurrency 与 prefetch 控制不同窗口 | 按序输出就没有并发、固定并发值适合所有池和负载 |
| Spring：[Programmatic Transaction Management](https://docs.spring.io/spring-framework/reference/data-access/transaction/programmatic.html) | TransactionalOperator 的事务范围与取消；Spring 5.3 起取消会触发回滚，多值结果需完整消费 | 任意事务框架都自动提供相同取消语义、本地事务覆盖远端命令 |
| Spring：[R2DBC](https://docs.spring.io/spring-framework/reference/data-access/r2dbc.html) 的 R2dbcTransactionManager | 事务连接绑定 subscriber Context，可由多条组合链共享 | 多个 Mono 意味着多个连接、切换线程后事务自动独立 |
| [R2DBC 1.0 规范](https://r2dbc.io/spec/1.0.0.RELEASE/spec/html/) §6 Connections / §7 Transactions | Connection 是带事务状态的会话；不保证多个订阅者并发修改状态安全 | 所有驱动行为完全相同、所有事务外读取都禁止并发 |

Reactor 的 current 文档会随版本变化，执行前以项目锁定版本核对；Spring R2DBC 用于解释资源共享，JetLinks 的实际事务实现、传播和取消仍须从当前框架确认。项目采用共享事务连接上串行数据库操作的开发约束，不能据此声称所有数据库驱动天生无法流水执行。

防止过度设计、重复校验、晦涩代码、魔法值与特调的文献解释统一见 [共享约束依据](../../jetlinks-conventions/references/design-constraint-sources.md)；本文件保留平台事实与评审案例，不将一般原则升级为无例外口号。

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

## 跨仓库历史评审依据

2026-11-16 从 `jetlinks-v2` 的 components、device、authentication、rule-engine、notify、web-core、device-ui、authentication-ui、collector、network 十个相关仓库抽取历史行内评审，每仓库最多四页、每页 100 条。样本共 1,780 条评论；按评论身份去重、排除回复与机器人后，1,185 条人工顶层意见涉及 340 个 PR，时间跨度为 2022-09 至 2026-11。不同仓库覆盖时间不一致，较早资料只提供历史线索。

主题先按文本初筛，再核对代表意见、相关调用路径和当前契约；一条意见可涉及多个主题，同一 PR 中重复意见不作为独立跨场景证据。这个有界样本用于排定审查重点，不是全组织缺陷统计，也不能证明每条旧意见今天仍成立。前端人工样本较少，前端规则同时依据真实组件代码与已有交互设计资料，不声称与后端具有相同评审覆盖。

| 反复出现的主题 | 代表评审 | 转为开发 / 审查约束时的边界 |
| --- | --- | --- |
| 职责错层、公共契约和重复实现 | [components #1593：管理接口职责](https://github.com/jetlinks-v2/jetlinks-components/pull/1593#discussion_r4582509517)、[authentication #394：命令归属](https://github.com/jetlinks-v2/authentication-manager/pull/394#discussion_r4409572346) | 按能力与变化原因确定 owner，不以开关隐藏错误落点，也不只移动文件 |
| 查询语义、嵌套条件和规模 | [components #1707：嵌套 / term](https://github.com/jetlinks-v2/jetlinks-components/pull/1707#discussion_r4510389308)、[collector #17：分页结构与全量](https://github.com/jetlinks-v2/collector-manager/pull/17#discussion_r4335975967)、[notify #81：动态 SQL](https://github.com/jetlinks-v2/notify-manager/pull/81#discussion_r4387640253) | 沿平台 DSL 核验行、count、筛选和数据边界；不能只要求“复用 QueryHelper” |
| 非 HTTP 入口的授权与 Context | [rule-engine #264：规则上下文](https://github.com/jetlinks-v2/rule-engine-manager/pull/264#discussion_r3974808424)、[notify #81：命令与 Controller 一致](https://github.com/jetlinks-v2/notify-manager/pull/81#discussion_r4421752270) | 各独立入口沿统一契约授权；不能重复所有内部检查，也不能只保护 Web |
| 推送、订阅、类型化事件与重复消息 | [authentication #359：统一 EventBus decode](https://github.com/jetlinks-v2/authentication-manager/pull/359#discussion_r4293410124)、[rule-engine #237：按身份去重](https://github.com/jetlinks-v2/rule-engine-manager/pull/237#discussion_r2785660742)、[notify #81：订阅职责](https://github.com/jetlinks-v2/notify-manager/pull/81#discussion_r4397680313) | 保持消息身份、维度 / Topic 和交付语义，不能把任意时间窗丢弃当通用幂等 |
| 热路径重复查询、编译和缓存旁路 | [authentication #359：逐次投递查询](https://github.com/jetlinks-v2/authentication-manager/pull/359#discussion_r4139794162)、[device #461：Registry 缓存](https://github.com/jetlinks-v2/device-manager/pull/461#discussion_r4376091055)、[collector #12：编译复用](https://github.com/jetlinks-v2/collector-manager/pull/12#discussion_r4058901331) | 找真实数据源与稳定定义，结合失效 / 版本和容量复用；不是一律加缓存 |
| 隐式转换、类型与配置含义 | [components #1710：序列化 / 转换](https://github.com/jetlinks-v2/jetlinks-components/pull/1710#discussion_r4523663374)、[device #443：隐式配置转换](https://github.com/jetlinks-v2/device-manager/pull/443#discussion_r3870789043) | 跨传输、存储和 UI 保持类型与用户语义；不靠 JSON 互转或默认值掩盖不匹配 |
| 业务耦合初始化与过早扩展 | [authentication #361：模板归启动模块](https://github.com/jetlinks-v2/authentication-manager/pull/361#discussion_r4060496559)、[authentication #359：不过度扩展参数](https://github.com/jetlinks-v2/authentication-manager/pull/359#discussion_r4132526621) | 业务数据由业务安装 / 选装拥有；扩展点应有真实需求，不能为通用性建立空框架 |
| 无用途统计、零值歧义和现有组件能力 | [rule-engine #279：列表次数与未开启](https://github.com/jetlinks-v2/rule-engine-manager/pull/279#discussion_r4523372763)、[device-ui #240：已有 tooltip](https://github.com/jetlinks-v2/device-manager-ui/pull/240#discussion_r3818655621)、[web-core #40：重复逻辑](https://github.com/jetlinks-v2/jetlinks-web-core/pull/40#discussion_r3152038417) | 信息须支持任务决策，成本和含义正确；已有组件契约能覆盖时不重复包装 |

新补充的状态流转、批量失败重放、历史 / 实时交接与运行资源路径还结合了当前平台源码，具体锚点与反例在 [场景链路](scenario-review-map.md)。它们不都具有相同历史出现频率，不把推导出的风险伪称为已统计的高频缺陷。规则仍只由对应开发技能维护。
