# 代码结构检索与多证据图规则

本文件定义稳定的检索决策和图语义。具体产品、版本和演进选型放在 [`tooling-and-research.md`](tooling-and-research.md)，避免工具变化污染日常执行规则。

## 1. 先定义问题，不先选工具

| 问题 | 首选事实源 | 典型输出 |
| --- | --- | --- |
| 精确字符串、配置、注解、Topic 片段 | `rg`、Git、构建文件 | 命中文件与行号 |
| 定义、引用、实现、类型层级 | LSP / 编译器语义 | 精确 symbol 和位置 |
| Maven 模块及第三方依赖 | reactor `pom.xml`、依赖树 | 模块边与依赖来源 |
| 一至数跳调用 / 引用路径 | 结构图 / SCIP，源码复核 | 有界路径与边置信度 |
| Command / Event / Topic / AssetsHolder 等领域流 | JetLinks AST 规则 + 配置 / 源码 | 领域边与注册依据 |
| changed paths 的影响面和候选测试 | Git diff + 反向边 + 覆盖率 | 消费者、风险和测试候选 |
| 数据流、污点、安全路径 | CodeQL / Joern / 运行时 trace | 路径、source / sink、限制 |
| “概念上相关”的代码或文档 | FTS / 语义检索 | 候选结果，不是精确关系 |

精确事实优先于相似度。语义检索只用于发现候选，不能证明符号引用、调用、依赖、覆盖或发布边界。

## 2. 检索漏斗

按信息增益与成本逐层升级：

1. **Git 与文本层**
   - 先读 task / Recovery Capsule 提供的路径、symbol 和 changed paths。
   - 使用 `rg --files`、`rg`、`git diff --name-only`、`git log -- <path>` 回答精确问题。
   - 通过根 / 聚合 `pom.xml`、`package.json`、workspace 配置确认工程和模块边界。
2. **符号语义层**
   - 查询 definition、references、implementations、type hierarchy、call hierarchy。
   - Java 使用构建 classpath 后的 JDT 语义；TypeScript 使用 tsserver / language service；Vue SFC 使用 Vue language tools 的虚拟代码与类型语义。
3. **持久结构图层**
   - 对多文件或跨层问题查询 callers、callees、imports、inheritance、flows、communities 和 impact radius。
   - 先检查 `repo_root`、branch / commit / tree、last update、节点数、语言覆盖和解析错误。
   - 从一个精确节点 1–2 hop 展开，默认限制返回节点、路径、文件和 token 数。
4. **JetLinks 领域关系层**
   - 补充通用符号图无法可靠表达的框架注册、消息、权限和前后端关系。
5. **深层分析 / 动态证据层**
   - 只有静态层不能区分候选根因时，使用 CodeQL、Joern、日志、TraceHolder、JFR、测试覆盖或最小运行时探针。

每次升级都说明上一层缺少什么事实。不要为了“更高级”而跳过低成本精确查询。

## 3. 最小多证据图模型

### 节点

```text
Repository, Module, Package, File, Type, Method, Field,
Endpoint, Command, Event, Topic, DatabaseTable,
VueComponent, Route, ApiClient, Test
```

### 边

```text
CONTAINS, DECLARES, IMPORTS, DEPENDS_ON_MODULE,
EXTENDS, IMPLEMENTS, REFERENCES, CALLS,
ANNOTATED_WITH, EXPOSES_ENDPOINT,
HANDLES_COMMAND, PUBLISHES_EVENT, SUBSCRIBES_TOPIC,
READS, WRITES, USES_COMPONENT, ROUTES_TO, CALLS_API,
TESTS, COVERS, CHANGED_WITH
```

不要把 `CALLS`、`SUBSCRIBES_TOPIC`、`DEPENDS_ON_MODULE` 和 `CHANGED_WITH` 合并成模糊的 `DEPENDS_ON`。方向和含义决定影响分析能否成立。

### 最小证据字段

每条边至少保留：

```text
source, target, kind, file, line,
extractor, evidence, confidence, confidence_tier,
repo_root, revision_or_tree, updated_at
```

置信度建议分层：

- `RESOLVED`：编译器 / LSP / 构建系统精确解析。
- `EXTRACTED`：AST 或明确配置直接抽取，但未做完整类型解析。
- `INFERRED`：框架约定、字符串拼接或名称匹配推断。
- `RUNTIME`：测试、trace 或实际执行观测；同时记录环境与输入。
- `AMBIGUOUS`：存在多个合法目标或证据不足。

运行时证据不自动比静态证据“更真”：它只证明特定输入、配置和环境下发生过。影响分析应保留多种证据来源，而不是覆盖旧边。

## 4. JetLinks 领域边

第一批领域抽取只覆盖高频且有稳定锚点的关系：

- Maven parent / aggregator / module 与软链接入口到真实模块。
- Controller endpoint → Service / Repository 与权限注解。
- `CommandSupport.execute(...)` / command id → command provider / handler。
- Event publish → listener；Topic publish → `@Subscribe` / 动态订阅候选。
- CRUD / 自定义接口 → `AssetsHolder.injectQueryParam`、`assertPermission`、`filterAssets` 与 `AssetType`。
- `ProtocolSupportProvider` → codec / parser / transport route。
- TraceHolder span → 所在业务阶段；MBean → 被管理的常驻组件。
- Vue route → page → component → API client → backend endpoint。
- `EnumDict` / `I18nEnumDict` → 前端 `{value,text}` 的展示 / 提交消费者。

领域抽取器应根据注解全名、类型解析、方法签名、常量传播和配置事实工作。只靠文件名 / 类名 / 字符串相似度的边标为 `INFERRED` 或 `AMBIGUOUS`，不得伪装成精确调用。

## 5. 面向智能体的有界查询契约

MCP 或其他检索接口优先提供少量高价值操作：

```text
find_symbol(query, kind?, module?, limit?)
find_references(symbol, limit?)
get_implementations(symbol, limit?)
get_callers(symbol, depth=1, limit?)
get_callees(symbol, depth=1, limit?)
get_type_hierarchy(symbol, depth=2, limit?)
trace_path(from, to, max_depth?, max_paths?)
get_module_dependencies(module, direction?)
get_domain_flow(anchor, kinds?, max_depth?)
get_change_impact(changed_paths, max_depth=2, limit?)
suggest_tests(changed_paths, limit?)
get_sibling_implementations(symbol, limit?)
explain_edge(edge_id)
```

查询结果必须：

- 包含稳定 symbol ID 或 qualified name、文件与行号。
- 带 relation kind、extractor、revision 和 confidence。
- 明确是否被 `limit` / token budget 截断。
- 默认返回摘要和少量锚点，不返回完整文件正文。
- 允许根据一个 edge / node 再扩一跳，而不是一次吐出全图。

## 6. 变更影响与测试推荐

1. 从 `git diff --name-only` 和 changed symbols 出发，不从全图最大 hub 出发。
2. 沿反向精确引用、实现 / 继承、模块依赖和领域消费者扩展。
3. 把静态候选与测试映射结合：直接测试、覆盖率边、同模块测试、Git co-change。
4. 输出“必须验证”“高置信候选”“低置信人工检查”三组，不把所有邻居都当必跑测试。
5. 与 `$jetlinks-delivery` 的证据账本对接：相关代码、测试、配置、依赖和环境指纹未变时复用已有结果；只补跑新影响面或失效证据。

覆盖率和 Git co-change 是历史 / 动态证据，不证明业务契约完整。没有覆盖关系也不等于没有影响。

## 7. 新鲜度和降级

使用索引前检查：

- 仓库根是否一致，是否错误落到父仓 / 子仓。
- 当前 branch、HEAD / tree 与 index revision 是否一致。
- changed files 是否已增量更新。
- 目标语言和文件类型是否被索引。
- 符号数量、边数量、解析失败和歧义率是否合理。

处理方式：

- 指纹匹配：直接做有界查询。
- 仅 changed files 未更新：增量刷新后查询。
- 目标文件 / 语言不支持：回退 LSP、构建事实和 `rg`。
- 图与源码冲突：源码 / 构建 / 运行时证据优先，记录图缺口。
- 索引需要完整重建：只在确有必要的阶段边界执行，不因每次编辑重复构建。

## 8. 与任务状态和系统性求解衔接

- 系统图是问题模型的查询结果，不是新的仓库权威文档。
- Recovery Capsule 只记录 3–7 个已确认的文件 / symbol / test 锚点、必要 edge / flow ID、index revision 和唯一下一查询；不复制整张图。
- 上下文恢复时先核对 Git 与索引指纹；一致则直接查询 capsule 指定节点，不重新扫描全仓。
- 若一次实现失败，比较运行时失败签名与原图假设。只有图漏边、置信度错误或假设被否定时才扩大检索，不机械重跑同一全图查询。
