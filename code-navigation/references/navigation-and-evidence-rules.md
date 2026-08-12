# 代码导航与证据规则

本文件定义与语言、代码托管平台和工具无关的检索决策、关系语义及查询契约。具体后端只作为可选能力，见 [`tooling-options.md`](tooling-options.md)。

## 1. 以问题选择证据能力

| 问题 | 所需能力 | 最小输出 |
| --- | --- | --- |
| 精确文本、配置、资源或路径 | literal / path search | 位置与匹配内容 |
| 定义、引用、实现、层级 | semantic symbol navigation | 稳定 symbol 与位置 |
| 组件及外部依赖 | build / package metadata | 有方向的依赖与声明来源 |
| 一至数跳调用或引用路径 | semantic or structural traversal | 有界路径与边证据 |
| 框架注册、消息、路由或资源流 | framework / domain extraction | 领域关系及注册依据 |
| changed items 的影响面与候选测试 | change set + reverse relations + test evidence | 消费者、风险和测试候选 |
| 控制流、数据流、污点或安全路径 | program analysis or runtime evidence | path、source / sink 与适用范围 |
| 概念相近的代码或文档 | full-text / semantic discovery | 候选结果，不是精确关系 |

先使用能直接回答问题的最低成本证据。只有当前层缺失会改变决策的事实时才升级，不以工具“更高级”作为升级理由。

## 2. 能力发现与降级

开始前识别当前环境实际具备的能力：

- 用户、任务状态或恢复制品提供的文件、symbol、测试、变更集或路径锚点。
- 可用的精确文本 / 路径搜索、版本历史或工作树差异能力。
- 构建、包管理、模块清单或依赖锁定信息。
- 编译器、语言服务、语义索引、语法树或结构索引。
- 框架 / 领域 extractor、覆盖率、trace、日志或可控测试。

缺失某层时按证据能力降级，而不是报错或擅自安装：

- 无版本控制：以工作区根、文件内容摘要、构建配置或任务 revision 建立 source fingerprint。
- 无语义导航：使用精确声明 / 导入搜索、构建事实和源码复核，并降低置信度。
- 无结构图：从单个 symbol 手工沿生产者与消费者有界扩展。
- 不支持目标语言 / 生成文件：使用该语言实际可用的编译器、构建产物、生成配置或运行时证据。
- 无运行环境：给出静态证据边界和最小待执行验证，不把静态候选描述为已发生事实。

读取现有能力和索引属于发现；安装工具、修改全局 / 项目配置、启动常驻服务或生成大体量索引属于状态变更，只有任务明确要求或实施范围确实包含它时才执行。

## 3. 检索漏斗

1. **已有锚点**：任务目标、恢复制品、错误位置、变更项、测试名、用户给定 symbol。
2. **精确事实**：路径、literal、配置、历史、构建 / 包声明。
3. **符号语义**：definition、references、implementations、type hierarchy、call hierarchy。
4. **结构关系**：语法 / 语义图中的跨文件关系、反向影响和路径候选。
5. **框架与领域关系**：注册、消息、路由、权限、资源、生成器和动态配置。
6. **深层或动态证据**：控制 / 数据流分析、覆盖率、trace、日志或最小运行时探针。

每次只扩展能区分当前候选或决定下一动作的一层。默认从一个锚点和一跳关系开始；具体深度、文件数、节点数和输出预算按任务风险与环境容量设置，不固定为某个仓库规模。

## 4. 通用多证据图

图不是必需基础设施，而是统一表达查询结果的逻辑模型；可以由内存结构、文本结果、索引文件、关系表或图数据库承载。

### 节点

```text
Workspace, Component, Package, File, Symbol, Type, Callable,
DataObject, Resource, Endpoint, Message, Route, Test
```

领域扩展可以新增有明确定义的节点类型，但不得用不透明字符串代替稳定标识。

### 边

```text
CONTAINS, DECLARES, IMPORTS, BUILD_DEPENDS_ON,
EXTENDS, IMPLEMENTS, REFERENCES, CALLS,
REGISTERS, PRODUCES, CONSUMES,
READS, WRITES, ROUTES_TO,
TESTS, COVERS, CO_CHANGES_WITH
```

领域扩展可以新增边类型；必须声明方向、证据来源、动态性和可否用于反向影响分析。

### 最小证据字段

```text
source, target, kind, locator,
extractor_or_capability, evidence,
confidence, confidence_tier,
workspace_id, source_fingerprint, observed_at
```

`source_fingerprint` 使用当前环境可提供的稳定身份，例如 revision / tree、change-set ID、构建快照、内容摘要或任务 revision；不能强制要求某一种版本控制标识。

### 置信度

- `RESOLVED`：编译器、语言服务或构建 / 包系统精确解析。
- `EXTRACTED`：语法树或明确配置直接抽取，但未完成全部语义解析。
- `INFERRED`：命名、约定、构造字符串或框架规则推断。
- `RUNTIME`：在记录的输入、环境和配置下实际观测。
- `AMBIGUOUS`：存在多个合法目标、覆盖不完整或证据冲突。

运行时证据只证明其观测范围；静态精确边也不证明运行时一定经过。保留多种证据，不用后来的边无条件覆盖原证据。

## 5. 有界查询契约

无论后端工具如何命名，优先映射到以下逻辑操作：

```text
find_symbol(query, filters?, limit?)
find_references(symbol, limit?)
find_implementations(symbol, limit?)
get_callers(symbol, depth?, limit?)
get_callees(symbol, depth?, limit?)
get_hierarchy(symbol, depth?, limit?)
trace_path(from, to, max_depth?, max_paths?)
get_component_dependencies(component, direction?)
get_domain_flow(anchor, relation_kinds?, max_depth?)
get_change_impact(changed_items, max_depth?, limit?)
suggest_tests(changed_items, limit?)
find_sibling_implementations(symbol, limit?)
explain_relation(relation_id_or_tuple)
```

结果必须：

- 返回当前环境可稳定重定位的 symbol / file / range 或资源 locator。
- 标明 relation kind、证据能力、source fingerprint 和 confidence。
- 标明截断、未索引、未解析、多个候选和不支持的范围。
- 默认返回摘要和少量锚点，不返回整仓正文或完整图。
- 支持从结果继续扩一跳，不要求一次查询解决所有问题。

若后端不提供某个逻辑操作，用可用能力组合出最小结果，并如实降低置信度；不要虚构工具调用或精确度。

## 6. 变更影响与测试候选

1. 从当前环境提供的 changed files / symbols / resources 或用户指定改动出发。
2. 沿反向精确引用、实现 / 继承、构建依赖和已定义领域消费者扩展。
3. 结合直接测试、覆盖率、同组件测试和历史共变等不同证据。
4. 分成“必须验证”“高置信候选”“低置信人工检查”，不要把所有邻居都当必跑测试。
5. 已有测试证据仍覆盖当前 source fingerprint 和相关输入时可以复用；只补跑新影响面、失效证据或有时效性的检查。

覆盖率与历史共变是辅助证据：没有覆盖或共变关系不等于没有影响，存在关系也不证明业务契约已完整验证。

## 7. 新鲜度与冲突

使用现有索引或缓存前检查：

- workspace identity 与 root / scope 是否匹配。
- source fingerprint 是否覆盖当前源码或 change set。
- 目标语言、生成物、配置和文件类型是否受支持。
- 节点 / 关系数量、解析失败、歧义率和截断是否合理。

处理顺序：

- 指纹匹配：直接有界查询。
- 少量变更未覆盖且后端支持：增量刷新。
- 目标范围不支持：降级到更基础能力。
- 索引与当前源码 / 构建事实冲突：当前事实优先，并记录索引缺口。
- 只有索引身份失配、系统性损坏或大范围结构变化使增量更新不可信时，才考虑完整重建。

上下文压缩、需要多看一个调用方或单条推断边需复核，都不是完整重建理由。

## 8. 任务与恢复衔接

- 查询结果是任务证据，不自动成为仓库权威文档。
- 若当前任务系统支持恢复状态，只记录少量文件 / symbol / test locator、必要 relation / flow handle、source fingerprint 和唯一下一查询；不复制整张图。
- 恢复时先核对任务与 source fingerprint。一致则从记录锚点继续；不一致时只扩大到解释失配所需的范围。
- 失败后比较新失败签名与原关系假设。只有证据否定假设、暴露漏边或关系置信度不足时才扩大检索，不机械重复相同扫描。
