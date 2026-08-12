# 工具选型与研究依据

本文件只在设计、安装、评测或替换检索后端时读取。版本、许可证和维护状态在实际采用前仍需以当时官方资料复核。

## 1. 推荐架构

面向 JetLinks Java/Maven + Vue/TypeScript 工作区，优先采用：

```text
rg / Git / build manifests
        ↓
JDT LS + TypeScript language service + Vue language tools
        ↓
incremental SQLite structural graph / SCIP index
        ↓
JetLinks-aware AST domain edges
        ↓
CodeQL / Joern / runtime trace on demand
```

当前若已经安装 `code-review-graph`，可先复用其 Tree-sitter 增量索引、SQLite、本地 MCP、调用 / 影响查询和 edge confidence，避免新建图平台。其结构关系仍需按源码或 LSP 复核，领域边宜作为独立 extractor 扩展；不要因已有工具就把它当唯一真相源。

## 2. 工具比较

| 能力 | 适合做什么 | 主要限制 | 建议阶段 |
| --- | --- | --- | --- |
| `rg` + Git | 精确文本、changed paths、历史、配置 | 不理解类型和动态关系 | 必选基础层 |
| Maven reactor / dependency tree | 模块与第三方依赖 | 不提供业务调用 / 事件流 | MVP |
| Eclipse JDT LS | Java definition、references、implementations、hierarchy、call hierarchy | 需正确 classpath；框架动态边有限 | MVP |
| TypeScript language service | TS / JS 符号和类型导航 | Vue SFC 需专门集成 | MVP |
| Vue language tools | Vue SFC 虚拟代码、类型检查与 language server | runtime registration 仍可能不确定 | MVP |
| `code-review-graph` | 本地增量结构图、MCP、有界遍历、impact、flow、confidence | Tree-sitter / 推断边不等于编译器语义 | 可直接试点 |
| SCIP + scip-java / scip-typescript | 持久化跨文件定义、引用、实现索引 | Java indexer 官方状态仍标为 development；Vue 领域关系需补充 | 二期 / 跨仓 |
| JavaParser / Spoon | 自定义 Java AST / 符号规则和领域抽取 | 需维护规则与 classpath，不能替代所有动态证据 | 领域图二期 |
| Tree-sitter | 多语言快速语法抽取 | 单独无法可靠解析重载、动态分派和 classpath | 结构候选层 |
| Semgrep | 模式、规则和部分数据流检查 | 不是完整代码导航 / 依赖图 | 定向规则 |
| CodeQL | 跨过程数据流、污点、安全与复杂查询 | 建库和查询成本较高；CLI 闭源分析有单独许可约束 | 高价值深查 |
| Joern | Code Property Graph、数据 / 控制流研究 | 部署、查询与资源成本较高 | 特殊深查 |
| Sourcegraph | 跨仓持久索引、搜索与导航产品化 | 平台运营、权限和成本 | 多仓规模明确后 |
| Neo4j / JanusGraph | 大规模共享图、多跳分析与可视化 | 对单机智能体 MVP 过重 | 指标证明需要后再上 |

SQLite / DuckDB 邻接表足以支持第一版有界查询。先测节点 / 边规模、更新耗时、查询延迟、歧义率和任务收益，再决定是否迁移图数据库。

## 3. 分阶段落地

### MVP：可用而非完美

- Maven module graph 与 Git changed paths。
- Java / TypeScript / Vue 的精确 symbol navigation。
- 本地增量 SQLite 图缓存。
- `find_symbol`、references / callers / callees、module dependencies、change impact、suggest tests 等 8–12 个有界查询。
- 所有结果带 file / line / revision / confidence；索引自动生成物保持 Git-ignored。

### JetLinks 领域图

- Command、Event、Topic、AssetsHolder、Protocol、TraceHolder / MBean、Vue route / API、EnumDict 消费边。
- 领域 extractor 以测试夹具固定真实注解、常量拼接、重载、多个 handler、动态 topic 和反例。
- 将通用结构边与领域边分开存储和评测，避免规则污染所有 Java 项目。

### 高级分析

- 引入覆盖率边与运行时 trace，校准静态候选。
- 需要跨仓精确导航时评估 SCIP / Sourcegraph。
- 需要安全 / 数据流问题时按查询启用 CodeQL 或 Joern，不把高成本建库放进每次任务起手式。

## 4. 面向智能体的评测

不要只评测“建图成功”。用一组真实任务比较开启 / 关闭结构检索：

- 首次找到 owning symbol / root cause 的时间。
- 首次有效生产修改前读取的无关文件数和 token 数。
- 正确定位生产者、消费者和同类实现的召回率。
- 错误边 / 歧义边导致的错误修改率。
- 上下文压缩后重复扫描率和恢复到正确 `Next` 的时间。
- 变更影响候选的 precision / recall 与漏测率。
- 任务成功率、返工轮数、同一假设下重复补丁数。
- 索引全量 / 增量耗时、存储、峰值内存和查询 p95。

结构检索必须证明它减少了无关阅读和错误定位，而不是只生成更漂亮的图。

## 5. 文献与官方资料

- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills)：focused skills、渐进披露、明确触发边界和真实 prompt 测试。
- [OpenAI：Hooks](https://learn.chatgpt.com/docs/hooks)：`PreCompact` / `PostCompact`、`SessionStart`、`PostToolUse` 等生命周期点可用于刷新恢复胶囊、增量索引和轨迹采集；确定性强制规则宜用 hook，而不是只靠自然语言提醒。
- [SWE-agent / Agent-Computer Interface](https://arxiv.org/abs/2405.15793)：工具接口和高信息密度反馈会直接影响代码代理表现。
- [AutoCodeRover](https://arxiv.org/abs/2404.05427)：AST 级 class / method 搜索与测试故障定位可减少代码搜索空间。
- [Agentless](https://arxiv.org/abs/2407.01489)：定位—修复—验证的简单分阶段流程可以成为强基线，避免把编排复杂度误认为问题解决能力。
- [CodeMonkeys](https://arxiv.org/abs/2501.14723)：并行候选和测试选择能提高部分任务成功率，但计算成本较高，应以评测决定启用范围。
- [SCIP](https://github.com/sourcegraph/scip)：语言无关的持久 code navigation 索引，面向 definition、references 和 implementations。
- [Eclipse JDT LS](https://github.com/eclipse-jdtls/eclipse.jdt.ls)：基于 Eclipse JDT 的 Java language server。
- [Vue language tools](https://github.com/vuejs/language-tools)：Vue SFC language server、language service 与 TypeScript 插件。
- [CodeQL](https://github.com/github/codeql)：标准查询与库为 MIT；CodeQL CLI 单独授权，闭源分析采用前需复核商业许可。
- [Joern](https://github.com/joernio/joern)：Code Property Graph 平台，适合代码、控制流与数据流组合查询。
- [code-review-graph](https://github.com/tirth8205/code-review-graph)：本地 Tree-sitter / SQLite / MCP 增量结构图；其自述评测与功能声明属于项目方证据，试点时应在 JetLinks 真实任务上独立复现。

研究结论不覆盖工作区事实。每个工具当前支持的语言、版本、许可证、资源消耗和索引质量都应在引入时重新核对。
