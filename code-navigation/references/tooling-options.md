# 可选检索后端与评测

本文件仅用于选型、安装、替换或评测后端，不是日常检索的必读清单。下列产品是能力示例，不是默认依赖；采用前必须根据当前语言、仓库规模、部署环境、权限、维护状态、许可证和成本重新核对官方资料。

## 1. 先按能力选型

| 能力层 | 可选实现示例 | 选择条件 | 常见限制 |
| --- | --- | --- | --- |
| 精确文本 / 路径 | ripgrep、IDE 搜索、平台代码搜索 | 已知名称、literal 或路径 | 不理解类型和动态关系 |
| 版本 / 变更事实 | Git、其他 VCS、平台 change set API、内容摘要 | 需要 revision、diff 或历史 | 环境可能没有 VCS 或历史 |
| 构建 / 包依赖 | Maven / Gradle、npm / pnpm、Cargo、Go modules 等原生工具 | 需要组件与外部依赖事实 | 不等于业务调用图 |
| 语义符号 | 各语言 compiler / language server，例如 JDT LS、clangd、rust-analyzer、gopls、TypeScript / Vue language tools | 项目能建立正确编译 / 类型上下文 | 动态框架关系仍不完备 |
| 持久代码导航 | SCIP / LSIF indexer、Sourcegraph 等 | 需要跨文件、跨仓持久 definition / references | 索引器语言覆盖和运营成本不同 |
| 多语言结构图 | Tree-sitter 类抽取器、`code-review-graph` 等 | 需要快速结构候选与有界遍历 | 语法 / 推断边不等于编译器语义 |
| 自定义 AST / 领域边 | compiler API、JavaParser、Spoon、TypeScript compiler API 等 | 框架 / 领域关系有稳定锚点 | 需要维护 classpath、规则与测试 |
| 规则与数据流 | Semgrep、CodeQL、Joern 等 | 需要模式、控制 / 数据流、污点或安全分析 | 建库、查询、资源和许可成本可能较高 |
| 运行时证据 | tests、coverage、trace、profiler、logs | 静态证据无法区分动态目标或时序 | 仅覆盖实际输入与环境 |

不要从列表顺序推导默认产品。先定义问题和所需证据，再检查当前环境是否已有匹配能力；缺失时优先降级，只有用户或实施范围授权时才安装或配置。

## 2. 存储形态

结构关系不必落图数据库：

- 单次小查询：内存或直接工具结果即可。
- 单仓增量索引：文件索引、嵌入式关系表或等价本地存储通常足够。
- 多仓共享、复杂并发多跳和图运维需求明确：再评估服务化索引或图数据库。

用节点 / 边规模、增量耗时、查询延迟、并发、权限隔离、备份与维护成本证明升级需要；不要因为可视化需求单独引入重型平台。

## 3. 后端接口原则

- 通过能力接口映射 `find_symbol`、references、hierarchy、trace path、impact 和 tests，不让技能依赖供应商工具名。
- 工具声明只暴露任务所需的少量查询，避免大量 MCP schema 占用上下文。
- 返回稳定 locator、source fingerprint、provenance、confidence 和截断信息。
- 索引刷新与查询分离；不在每次搜索或编辑后自动全量重建。
- 安装、注册 MCP、修改项目配置或启动 watcher 应是明确部署动作，不应由日常导航技能静默执行。

## 4. 评测

不要只测“能否建图”。至少比较启用 / 禁用某后端时：

- 找到 owning symbol / root cause 的时间。
- 首次有效修改前的无关文件数和上下文量。
- 生产者、消费者、同类实现和候选测试的 precision / recall。
- 错误 / 歧义关系导致的错误修改率。
- 上下文恢复后的重复扫描率和回到正确下一步的时间。
- 任务成功率、返工轮数与同一假设下重复补丁数。
- 全量 / 增量索引耗时、存储、峰值资源和查询 p95。

后端必须证明它减少无关阅读和错误定位，而不是只生成更多节点或更漂亮的图。

## 5. 资料

- [OpenAI：Build skills](https://developers.openai.com/codex/build-skills)：focused skills、渐进披露、明确触发边界和真实 prompt 测试。
- [OpenAI：Hooks](https://developers.openai.com/codex/hooks)：生命周期 hook 可用于可选的索引刷新、恢复状态和轨迹采集；这不意味着任何运行时都必须提供 hook。
- [SWE-agent / Agent-Computer Interface](https://arxiv.org/abs/2405.15793)：工具接口和高信息密度反馈会直接影响代码代理表现。
- [AutoCodeRover](https://arxiv.org/abs/2404.05427)：AST 级 class / method 搜索与测试定位可缩小代码搜索空间。
- [Agentless](https://arxiv.org/abs/2407.01489)：定位—修复—验证的简单分阶段流程可作为强基线。
- [Deterministic Anchoring](https://arxiv.org/abs/2606.26979)：轻量调用 / 继承拓扑主要提升导航纪律与复现性，而不是要求把整张图灌入上下文；最佳粒度随仓库密度变化，大仓库应主动裁剪低价值前向边。
- [LARGER](https://arxiv.org/abs/2605.16352)：从 lexical match 对齐到高置信结构锚点，再在现有检索循环中扩展局部邻域；其实现不要求外部图数据库或专用图界面，支持“精确锚点 + 置信过滤 + 有界扩展”的通用契约。
- [SCIP](https://github.com/sourcegraph/scip)：语言无关的持久 code navigation 索引格式。
- [Language Server Protocol](https://microsoft.github.io/language-server-protocol/)：语言工具与客户端之间的通用协议。
- [CodeQL](https://github.com/github/codeql)、[Joern](https://github.com/joernio/joern)、[Semgrep](https://github.com/semgrep/semgrep)：不同深度的规则、控制流和数据流实现；采用时分别复核许可和支持范围。

研究与产品自述不覆盖当前工作区事实。不要把评测作者的机器、已安装命令、仓库路径、数据库文件或单次性能结果写成通用技能约束。
