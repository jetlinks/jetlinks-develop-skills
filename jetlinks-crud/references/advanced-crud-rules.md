# JetLinks 高级 CRUD 与查询规则

本文件处理“标准 CRUD 之外”的情况，包括复杂查询、批处理、数据同步和性能敏感逻辑。

## 何时使用

- 需要 `createQuery`、`createUpdate`、`createDelete`
- 需要 QueryHelper、分页转换、聚合查询、关联查询
- 保存或删除后需要同步其他数据
- 需要避免逐条更新、重复查询、阻塞式拼装

## 核心原则

1. 先复用当前模块已有查询方式
   - 有 `createQuery` 就优先用它。
   - 有 QueryHelper 或专用查询抽象，就跟随它。
   - `createQuery()` / `createUpdate()` / `createDelete()` / `QueryParamEntity` / `QueryHelper` 的细节见 [`query-dsl-rules.md`](query-dsl-rules.md)。

2. 联动按一致性选择 owner 与时机
   - 本地不变量留在原事务；不以 Service 长度或“保存后”为由改成异步事件。
   - 对外交付按 [事件规则](../../jetlinks-events/references/event-driven-rules.md#提交投递与恢复) 判断提交边界与恢复，单一步骤不必新增事件体系。

3. 批处理优先批量化
   - 批量更新、批量删除、分页转换、缓冲处理，尽量避免 N 次往返。

4. 复杂 SQL 先走 QueryHelper
   - 跨表、聚合、动态列、分页转换、原生 SQL 分析或执行，优先找 `QueryHelper` / `DefaultQueryHelper` / 当前模块封装。
   - 不拼接动态 SQL 字符串来覆盖条件组合，避免 SQL 数量随筛选项膨胀。
   - SQL 默认按标准 SQL 和多数据库兼容设计；除非用户明确限定数据库或模块已有明确限定，不写特定数据库方言。
   - 只有当前模块已有成熟模式或 DSL / QueryHelper 明显无法表达时，才使用原生 SQL。
   - 确需数据库方言时，在已有契约或 PR 中说明支持范围和真实兼容风险，不为此强制新建设计稿或无用途回退。

5. 多查询组合先走 QueryHelper
   - 分页转 DTO 优先 `QueryHelper.transformPageResult(...)`。
   - 一对多父子装配优先 `QueryHelper.combineOneToMany(...)`。
   - 普通 QueryParam 分页优先 `QueryHelper.queryPager(queryParam, repository::createQuery)` 或当前模块等价封装。

6. SQL 性能按真实场景验证
   - 写 SQL 时先估算真实数据量、筛选组合、排序字段、分页深度、索引命中和并发访问。
   - 只有本次改变查询形态、预期规模、索引、分页深度、并发、批量大小或资源风险时，才选择相称的执行计划、压力测试或等价性能验证；技术形态本身不触发压测。
   - 已确认风险需要压测但环境不可用时，说明替代验证和剩余风险；没有性能风险变化时不准备“不适用”证明。

## 推荐模式

### 查询结果与业务含义

- 过滤、权限、分页、count 和汇总覆盖相同业务范围；关联展开不能导致重复行、错 count 或先分页后远程剔除。自定义 term 保持嵌套 AND / OR、空值、否定和排序语义，不用手拼 SQL 复制通用查询能力。
- “不返回分页结构”不等于“查询全部”，是否取消分页沿平台请求契约单独表达。树、分类统计与关联数量按定义处理子级、去重和权限，不把查询逻辑藏进响应 DTO。
- 默认值须保留业务差异：真实 0、未开启、无权限、无样本、未知和读取失败不能混为一谈。列表 / 报表只加入有用途且可承受成本的信息，不逐项补查巨大历史来凑展示字段。
- 查询模型、字段类型和结果映射沿当前 DSL / QueryHelper；公共后端提供稳定条件语义，具体页面的筛选组合不靠场景特判 API 实现。

### 导入导出与批量失败

- 先确定整批原子、分批提交还是逐项结果契约；批量写入失败后回退单条，必须确认前次无已提交副作用或存在足够幂等保障，不能将重放当作天然安全的容错。
- 分批 / 部分成功时准确返回原输入身份、成功、失败和可重试范围；不能把失败吞掉后统一显示成功，也不能让一次取消自动撤销已提交批次。
- 大文件、导入流、导出、聚合和父子装配保持合理分页 / 批次 / 内存边界；读取、解析、转换与写入沿既有能力，正确释放流、文件和 DataBuffer。新增上限应来自实际数据 / 资源契约，不任意拒绝合法数据。
- 文件入口仍是独立业务入口，沿通用权限、字段可读写、校验及类型转换契约；列标题国际化不改变稳定字段路径，导出不能绕过数据权限或扩大敏感字段。
- 重试、批次进度和错误定位与后端实际提交状态一致。既有导入 helper 的 fallback / buffer 只是能力，不代替应用选择事务与幂等语义。

### 动态查询

适用：
- 用户传入 QueryParam
- 需要组合条件、排序、分页

要求：
- 保留现有查询体系，不自创请求协议
- 优先让查询对象驱动仓储或服务层

### 批量更新 / 删除

适用：
- 保存后回填名称、清理关联数据、统一状态变更

要求：
- 优先使用批量 `createUpdate` / `createDelete`
- 清空字段用 `setNull(...)`，不要写特殊占位值
- 可选字段用 `when(...)`，不要复制多套更新链路
- 必须带明确 `where` 条件后再 `execute()`
- 如在事件中触发，注意避免再次触发同类事件形成循环

### 分页结果转换

适用：
- 实体页转 DTO 页
- 需要在分页保持元信息的前提下转换数据项

要求：
- 优先复用当前模块已有分页转换工具
- JetLinks 常见场景优先 `QueryHelper.transformPageResult(...)`

### 父子数据装配

适用：
- 分页父列表补子列表
- 树 / 分组 / 标签等一对多关系回填

要求：
- 优先 `QueryHelper.combineOneToMany(...)`
- 不在 `flatMap` 中对每个父对象逐个查询子集合
- 不自己复制分页元信息或手写易错的 `groupBy` / `collectMap`，除非当前模块已有更明确封装

### 联动同步

适用：
- 分类名回填
- 删除上游实体后清理下游记录
- 关系变化后同步冗余字段或缓存

要求：
- 先判断一致性与交付承诺；必须原子完成的本地联动留在事务，外部交付按 [事件规则](../../jetlinks-events/references/event-driven-rules.md) 选择时机与恢复。
- 能批量处理就批量处理

## 何时联动到其他规则

- `createQuery()`、`QueryParamEntity`、排序、嵌套条件、分页、AssetsHolder 查询注入：继续读取 `query-dsl-rules.md`
- `createUpdate()`、`createDelete()`、`setNull(...)`、批量更新 / 删除：继续读取 `query-dsl-rules.md`
- `QueryHelper`、复杂 SQL、原生 SQL、分页结果转换、一对多组合：继续读取 `query-dsl-rules.md`
- 自定义 `termType`、动态条件、关联表 exists 查询：继续读取 `dynamic-term-rules.md`
- 跨模块能力调用：读取 [应用 / 平台边界](../../jetlinks-boundary/references/application-platform-rules.md) 与 [命令调用](../../jetlinks-boundary/references/cross-service-call-rules.md)
- 生命周期副作用：读取 [事件规则](../../jetlinks-events/references/event-driven-rules.md)
- 实时消息流处理：读取 [订阅规则](../../jetlinks-events/references/realtime-subscription-rules.md)

## 自检清单

- 查询方式是否沿用了当前模块现有抽象
- 复杂 SQL / 原生 SQL 是否优先评估了 QueryHelper，而不是拼接动态 SQL
- SQL 是否避免了无明确依据的数据库方言，并尽量兼容标准 SQL
- 查询形态、规模、索引、分页、并发或批量风险变化时，是否已有相称的执行计划、压力测试或等价性能验证
- 分页转换和一对多组合是否优先用了 QueryHelper
- 本地不变量是否仍在事务内，外部交付是否符合实际提交与恢复契约
- 是否避免了逐条阻塞调用
- 是否避免了无根据的原生 SQL
- 是否考虑了重复触发、循环联动和批量性能
