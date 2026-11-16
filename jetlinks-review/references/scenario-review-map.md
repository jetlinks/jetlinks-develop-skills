# 场景链路与反例

以下按业务结果组织审查路径，来自平台代码和历史评审中可以反复迁移的机制。源码名称是证据定位示例，不是要求每个项目具备这些模块或照搬其实现；进入实际任务仍从目标版本与当前入口开始。样例说明应该核实什么，不宣称所列实现存在未修复缺陷。

## 查询、搜索、树和报表

- 沿请求条件 / 数据权限 → 查询编译 → 数据范围 → 排序分页 → 装配 / 汇总 → 展示追踪。核实“查哪些对象、count 算什么、是否展开子级、权限作用在哪里”，再看 SQL 和性能。
- 重点反例：先分页再过滤、关联后重复计数、嵌套 OR 放宽权限、不返回分页结构就默认全量、未知 / 未开启展示为 0、为每行摘要再查巨大历史。聚合与列表允许不同粒度，但差异要符合各自明确契约。
- 代码锚点：`device-manager` 的 `DeviceInstanceController.export(productId, ...)` 在同一路径组合权限、产品范围、配置及标签的分批装配；`notify-manager` 的 `SystemBulletinService` 与订阅端共同消费维度 / 投递语义。不能仅验证单个 repository 方法返回正确行。
- 规则 owner：[高级查询](../../jetlinks-crud/references/advanced-crud-rules.md)、[Query DSL](../../jetlinks-crud/references/query-dsl-rules.md)、[AssetsHolder](../../jetlinks-assets-permission/SKILL.md)。

## 写入、删除、导入与批量处置

- 沿输入 / 差异 → 业务不变量 → 实际写入 → 关联 / 投影 → 批次结果检查。确定整批事务、分批提交或逐项结果，识别已提交副作用，再决定能否重放。
- 重点反例：全量校验阻止无关 PATCH、删主记录却遗漏关联、批量失败后单条回退重复执行前次成功项、将局部失败显示为整批成功、取消后假称已回滚所有批次。
- 代码锚点：`jetlinks-components/io-component/.../ImportHelper.executeImport` 可按配置从 batch handler 回退到单条；这表明应用必须核实 handler 的事务与幂等契约，不是证明 fallback 本身有错。独立导出入口仍需追到权限和字段范围。
- 规则 owner：[校验范围](../../jetlinks-crud/references/common-crud-rules.md#校验范围与变化语义)、[批量与文件](../../jetlinks-crud/references/advanced-crud-rules.md#导入导出与批量失败)。

## 工单、审批、支付与人工动作

- 沿身份 / 关联对象 → 合法前态 → 并发仲裁 → 状态、回执和投影 → 后续动作检查。把请求身份、定义版本、执行轮次和操作者区分开，避免“任何状态都能保存”。
- 重点反例：先查再改没有 CAS、影响行数为 0 仍成功、同幂等键不同载荷返回旧回执、只用一个对象 ID 去掉全部后续合法动作、迟到 Worker 把取消 / 新版本覆盖。
- 代码锚点：`jetlinks-workflow` 的 `WorkflowTaskService.complete / previousSubmission / submitAndAdvance` 将重复请求、输入比较与推进联系起来，`runtime/WorkflowTransitions.commit` 仲裁 revision 和写入；`jetlinks-inspection` 的 `InspectionOperationService.execute` 同时涉及对象锁、动作权限和操作回执。必要校验不能因代码较长被当成重复删除。
- 规则 owner：[状态与重复请求](../../jetlinks-crud/references/common-crud-rules.md#状态流转与重复请求)、[调用恢复](../../jetlinks-boundary/references/cross-service-call-rules.md#结果失败与恢复)。

## 跨服务命令、第三方适配与回调

- 沿调用方身份 → 能力发现 / 路由 → 提供方授权 → 真正副作用 → 响应解释 / 恢复检查。核实超时发生时结果是失败还是未知，谁能查询回执、谁拥有重试。
- 重点反例：exists 当授权、optional empty 当执行成功、合法业务 empty 当不支持、发送后换节点重试造成重复副作用、消息中一个 actor 字段就被提升为可信身份。内部本地 SPI 与跨服务调用也不能混为一谈。
- 代码锚点：`jetlinks-components/common-component/.../CommandContextSerializeSupport` 是上下文查找与 RPC 执行交接处；`jetlinks-payment` 的 `PaymentNotifyService.doNotify / executeNotifyBatch` 涉及命令 / HTTP 结果、重试队列与通知状态。读到重试代码还需追踪待办如何入队、出队、受理与恢复。
- 规则 owner：[平台边界](../../jetlinks-boundary/references/application-platform-rules.md)、[命令调用](../../jetlinks-boundary/references/cross-service-call-rules.md)、[授权](../../jetlinks-assets-permission/SKILL.md)。

## 事件、通知与可靠投递

- 沿状态提交 → 事件产生 → 持久受理 / 派发 → 处理 / ACK → 重试和幂等检查。区分本地原子性、事件时机和崩溃后可靠性。
- 重点反例：本地必须一致的关联清理被移到事务外、发了提交后事件就声称不会丢、受理回执被当业务完成、按时间窗去重误吞不同告警、无消费者还强行安装异步追踪链。
- 代码锚点：`jetlinks-workflow` 的 `WorkflowInboxDeliveryProvider.create` 返回持久受理结果，实际执行由流程侧继续；`WorkflowTransitions` 负责状态 / 历史和提交后唤醒，外部调用不放在该写事务。它们说明“成功”存在不同阶段，不要求所有事件都采用可靠投递。
- 规则 owner：[提交、投递与恢复](../../jetlinks-events/references/event-driven-rules.md#提交投递与恢复)。

## 历史加实时、告警订阅与重连

- 沿授权与 Topic → 建订阅 / 读历史 / 快照 → 交接 → 增量更新 → 断线 / 撤权 / 取消检查。识别流是最新状态、可靠事件还是历史记录，决定合并与背压。
- 重点反例：历史查询和实时订阅之间漏数据、旧快照覆盖新值、所有流统一丢旧值、多个 Provider 各自刷新认证、无匹配维度退回全量订阅、重连自动重做有副作用动作。
- 代码锚点：`things-component/.../MetricResultStream.watch / merge` 组合历史、初始值和更新并发出 ready；`rule-engine-manager/.../AlarmSubscriptionProvider.subscribe` 基于请求认证选择资产 / 维度路径并去重。审查交接与去重的业务含义，不照抄某个操作符形状。
- 规则 owner：[连续流](../../jetlinks-events/references/realtime-subscription-rules.md#连续流的语义与生命周期)、[响应式事务与并发](../../jetlinks-reactive/SKILL.md)。

## 规则、指标、流程、调度与热更新

- 沿定义 / 配置 → 校验与编译 → 发布版本 → 运行实例 → 输入输出 → 停用 / 替换检查。核实执行身份、运行版本和何时真正生效，沿错误路径看新旧实例如何协调。
- 重点反例：每条数据重新解析 / 查配置、保存了但启动失败仍显示运行中、同一配置锁住所有设备、停用没有释放任务、旧执行回调覆盖新实例、规则内查库丢失授权上下文。
- 代码锚点：`rule-engine-manager/SceneService.enable / disabled / handleSceneSaved / handleEvent` 跨持久状态和运行引擎；`collector-manager` 的点位解析历史评审要求按定义预编译和复用。数据库状态正确不能单独证明运行状态正确。
- 规则 owner：[事件生命周期](../../jetlinks-events/SKILL.md)、[热路径与运行状态](../../jetlinks-conventions/references/runtime-state-rules.md)。

## 缓存、资源、历史与运维

- 沿事实来源 → 派生 key / 版本 → 并发读写 / 失效 → 容量 → 重配 / 关闭 / 恢复检查。区分可重建缓存、可靠待办和业务审计；检查内部诊断是否反过来改变业务结果。
- 重点反例：重复最新值存储、共享可变值串请求、迟到旧值覆盖最新、TTL 有而容量无界、页面卸载关闭共享连接、每次读都新增历史快照、用日志代替可靠回执，或为一列无用次数扫描全部历史。
- 代码锚点：`things-component` 的 `ScopedMetricLatestCache`、`InMemoryMetricLatestCache` 涉及作用域、键映射、容量和旧值判断；`WorkflowTransitions` 同事务记录精简业务历史，不能因减少留痕删除必要审计。
- 规则 owner：[运行状态与留痕](../../jetlinks-conventions/references/runtime-state-rules.md)、[追踪](../../jetlinks-conventions/references/tracing.md)、[MBean](../../jetlinks-conventions/references/mbean-observability.md)。

## 元数据、序列化、扩展与装配

- 沿声明 / schema → 解析 / 映射 → 跨服务传输 → 查询 / 写入 → UI 或插件消费检查。核实公开结构与运行能力不同，字段类型、嵌套、单位、枚举、null 和目标版本贯通。
- 重点反例：JSON 互转损失精度和类型、隐式转换配置改变用户含义、元数据发现就当远端可写、接口存在但遗漏新分页签名、全局缓存冻结某个用户的语言、扩展能力实际未装配。
- 代码锚点：声明式扩展的 `TableExtensionSupport / EntityExtensionRuntime` 在声明表、查询、装配和元数据间协调；`device-manager/DeviceMetricConfigMapper` 表明配置规范化属于明确数据契约，不能无依据自动更改配置含义。协议编解码进一步沿 [protocol](../../jetlinks-protocol/SKILL.md) 追上下行及应答关联。
- 规则 owner：[数据契约](../../jetlinks-conventions/references/responsibility-and-generality-rules.md#数据契约与配置)、[平台扩展版本](../../jetlinks-boundary/references/application-platform-rules.md#标准实体字段扩展)。

## 前端任务与异步状态

- 沿用户任务 → 当前对象 / 草稿 → 请求 / 订阅 → 后端提交结果 → 回显 / 修正检查。除了布局，还要确认选择有实际作用、失败可恢复、状态不串对象、交互沿平台组件契约。
- 重点反例：旧请求回写新对象或结束新 loading、联动配置拆成多个不完整提交、取消也触发保存、卸载后 debounce 继续回写、已有组件 tooltip / 权限再包一套、空值 / 失败被显示为正常 0。
- 代码锚点：`jetlinks-web-core` 的 `useInlineEditField.commit / blur / cancel` 使用 generation 和宿主提交契约；`useRequest` 与 `useWebSocket` 则应沿各自调用方核实重叠请求、重复订阅和清理，不能只看到 loading 或 onUnmounted 就认为生命周期闭环。
- 规则 owner：[web](../../jetlinks-web/SKILL.md)、[异步结果与持续交互](../../jetlinks-web/references/state-management-rules.md#异步结果与持续交互)。

## 安装、迁移与版本演进

- 沿首次安装、用户已修改数据、升级 / 回滚和外部调用方分析。区分平台能力注册、业务选装数据、持久化迁移与未发布 PR 的中间实现。
- 重点反例：平台启动创建特定客户模板、升级重置用户设置、字段删除未迁移、未发布别名保留多条分支、用旧文档 / 测试绕过当前行为验证。不能为少写代码删除已发布数据和兼容义务。
- 规则 owner：[初始化与通用性](../../jetlinks-conventions/references/responsibility-and-generality-rules.md)、[发布与验证](../../jetlinks-delivery/SKILL.md)。
