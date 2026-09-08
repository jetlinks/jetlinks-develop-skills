# JetLinks Develop Skills

JetLinks 团队自定义的 Codex skills 仓库。

仓库结构参考 `awesome-claude-skills` 这类可直接扫描的仓库约定，skill 目录直接位于仓库根目录，每个 skill 保持自包含，便于安装、分发和自动识别。

## Repository Layout

```text
jetlinks-develop-skills/
├── README.md
├── .github/
│   └── pull_request_template.md
├── jetlinks-router/
├── systematic-solving/
├── agent-orchestration/
├── task-continuity/
├── code-navigation/
├── scripts/
├── jetlinks-protocol/
├── jetlinks-conventions/
├── jetlinks-reactive/
├── jetlinks-routing/
├── jetlinks-crud/
├── jetlinks-assets-permission/
├── jetlinks-boundary/
├── jetlinks-events/
├── jetlinks-web/
├── jetlinks-capture/
└── jetlinks-delivery/
```

约定说明：

- 每个 skill 目录直接位于仓库根目录，方便被只做浅层扫描的工具自动发现。
- 每个 skill 目录只保留运行所需文件，例如 `SKILL.md`、`agents/`、`references/`、`scripts/`、`assets/`。
- 仓库级说明放在根 `README.md`，不要在 skill 目录里额外堆叠说明性文档。

## Available Skills

### `jetlinks-router`

总入口 skill，用于 JetLinks 二开场景下的任务分类与路由。

### `systematic-solving`

用于存在实质因果不确定、未决共享契约风险或无证据反复修补的问题，准入以 [Admission](systematic-solving/SKILL.md#admission) 为准。已明确的机械跨层实现、正常测试替身和已授权 retry 能力直接按领域规则推进；只有在诊断中掩盖未解释失败、替换争议边界或反复执行无法产生新信息的检查，才构成停滞信号。失败先区分生产契约、陈旧 oracle、无效 fixture、机械装配或未决原因；根据新证据决定补齐实现还是修正假设，不因一次失败自动重建理论。

### `agent-orchestration`

用于任意执行环境中的单 Agent / 多 Agent 动态路由、真实委派、能力分层、并行边界、Assignment Capsule、失败升级、Result Packet 集成和阶段验证。默认只有明确质量、关键路径或上下文隔离收益时才委派；一旦当前执行选择非 `SINGLE_OWNER` 且宿主允许，必须真实 dispatch、收集和集成，不能只输出 Agent 角色或提示词。模型档位由判断量、影响面和验收 oracle 的通用 `CapabilityFloor` 决定，不按角色固定。进入委派程序后，主智能体是控制面经理，只负责规划、协调、监督、接受结果和请求宿主级合并 / 阶段验证，不代替 Worker 编写或修复生产代码、测试、文档或审查结论；需要源码改动时重新派发有界 Worker。默认采用扁平拓扑：主智能体是唯一调度者，委派深度 1，叶子 Agent 在宿主支持时硬关闭继续委派，同时只运行 1–2 个切片。一次有效失败后升级或重构任务，不让弱模型通过换提示词反复重试。协议、安全、身份和必需验收可以作为硬门禁，文风、展示和可选 confidence 只作为软指导或离线指标。核心技能不依赖 Codex、具体模型、Trellis、Git 或本地路径。

### `task-continuity`

用于任意执行环境中的长任务计划压缩、上下文恢复、运行态与权威文档分流、验证证据复用及阶段性交付。模型主视图只保留 `Contract / Checkpoint / DecisionState / Resume`；匹配的压缩续跑最多一个身份批次，并在同一恢复轮直接执行精确 `first_allowed_action`，不得先完整重读技能、线程、工作区、重新确认计划或做 confidence-only 验证。只有 identity 或验收边界失配才定向快照恢复。Codex 宿主可显式启用 execution adapter，以任务 / 运行 / 工作区 / 契约绑定且幂等的机器收据约束阶段验证、Agent 接受和 whole-task 发布；未配置时保持 no-op。环境存在 VCS / review 时，阶段验证后只保留本地 checkpoint，整体完成后才统一 push 并更新一个 task-level review。

### `code-navigation`

用于任意语言、构建系统和代码仓库的环境无关代码导航。它先发现当前环境实际提供的路径 / 文本搜索、构建元数据、符号语义、结构索引和运行时证据能力，再按“精确锚点 → 已解析符号 → 高置信局部关系 → 必要动态证据”逐层扩展；默认不构建或注入完整依赖图，并按 source fingerprint 增量复用局部视图。不要求 Git、`rg`、特定 LSP、图数据库、MCP 或本机安装工具。JetLinks 的 Command / Event / Topic / AssetsHolder / Protocol 等领域关系由 router reference 按需扩展。

### `jetlinks-protocol`

用于协议包开发、协议阅读、传输编解码、二进制报文分析和联调排障。

### `jetlinks-conventions`

用于共享编码规范、注解/导入确认、命名约束、代码注释、i18n 判断与实现，以及 TraceHolder 链路追踪和 MBean 运维可观测性判断。

### `jetlinks-reactive`

用于响应式编程实践、非阻塞链路、批处理和 reactive 风险控制。

### `jetlinks-routing`

用于工作区结构发现、模块落点判断和新模块创建。

### `jetlinks-crud`

用于标准 CRUD、复杂查询、批量处理、CRUD 相关副作用，并在涉及数据权限时路由到 AssetsHolder 资产权限规则。

### `jetlinks-assets-permission`

用于 JetLinks 后端统一 AssetsHolder 数据权限控制，包括 AssetType、`@AssetsController`、`AssetsHolderCrudController`、`CorrelatesAssetsHolderCrudController`、`CrudAssetPermission`、查询注入、操作校验、关联资产、命令服务和订阅过滤。

### `jetlinks-boundary`

用于直接依赖、命令服务、代理和跨模块边界选择。

### `jetlinks-events`

用于领域事件、生命周期事件、Topic 订阅和消息流处理。

### `jetlinks-web`

用于 JetLinks 前端页面开发、组件/hook/utils 能力复用、函数封装与组件边界判断、目录落点判断、状态管理与类型质量约束；坚持业务优先、参考为辅，默认沿用 Ant Design 风格；页面壳层、首屏组织、信息架构或视觉节奏受影响时，先按 `$jetlinks-web` 内置页面分型规则建立页面交互方案档案，再进入实现；需要交互打磨时，遵循 `$jetlinks-web` 的交互与视觉优化规则，且最终界面必须面向终端用户而非开发者；用户可见字段展示名、标题、按钮和提示文案统一走国际化，可使用中文作为默认值。

### `jetlinks-capture`

用于任务结束后的知识沉淀判断、经验归档、playbook 生成，以及决定是否需要继续更新 prompt 或 skill。

### `jetlinks-delivery`

用于提交信息、提交命令、分支策略、后端设计与测试驱动门禁、验证证据有效性判定和 PR 描述整理；阶段证据仍覆盖最终代码且相关输入未变化时直接复用，不因进入交付阶段机械重跑整套测试。

## Scenario Routing

推荐按场景直接使用 focused skill，不确定时再走总入口：

- 不确定该用哪个 skill：`$jetlinks-router`
- 存在实质因果不确定、未决共享契约或无证据诊断循环：先按 [systematic-solving Admission](systematic-solving/SKILL.md#admission) 判断准入，再按需加入领域扩展与对应 skill；机械跨层不自动升级，长任务状态另由 `$task-continuity` 管理
- 只想设计或执行多 Agent / 大小模型协作：`$agent-orchestration`；未知根因先加 `$systematic-solving`，长任务再加 `$task-continuity`
- 只想压缩计划、恢复上下文、复用测试证据或约束阶段 / PR 生命周期：`$task-continuity`
- 只想检索定义 / 引用 / 调用链、组件依赖、领域流、变更影响或候选测试：`$code-navigation`
- 只想处理协议包、编解码、认证或二进制报文：`$jetlinks-protocol`
- 只想确认代码规范、导入、注释、i18n 判断、国际化实现、TraceHolder 埋点边界或 MBean 运维可观测性：`$jetlinks-conventions`
- 只想处理响应式链路：`$jetlinks-reactive`
- 只想找模块或新建模块：`$jetlinks-routing`
- 只想做 CRUD 或复杂查询：`$jetlinks-crud`
- 只想判断或实现 AssetsHolder 数据权限边界：`$jetlinks-assets-permission`
- 只想处理跨边界调用：`$jetlinks-boundary`
- 只想处理事件或订阅：`$jetlinks-events`
- 只想处理前端页面改造、能力复用、前端质量约束或在现有设计体系内优化交互：`$jetlinks-web`；若涉及页面壳层、首屏组织或信息架构，由其按内置页面分型规则先建立方案档案
- 只想判断是否值得沉淀知识：`$jetlinks-capture`
- 只想整理提交、设计门禁、测试和 PR：`$jetlinks-delivery`

## Codex Multi-Agent Adapter

通用 `$agent-orchestration` 不要求 subagent。仓库同时提供可选的 Codex 项目适配：

- [`.codex/config.toml`](.codex/config.toml) 显式开启主会话的多 Agent 能力，并使用官方仍支持的保守并发别名将项目级 subagent 上限设为 3；模型档位由各 Agent profile 负责。
- [`.codex/agents/bounded-explorer.toml`](.codex/agents/bounded-explorer.toml) 用于低成本只读证据检索。
- [`.codex/agents/mechanical-worker.toml`](.codex/agents/mechanical-worker.toml) 用于已冻结契约、验收确定且写集独占的低影响机械修改；首次有效失败后升级，不重试猜测。
- [`.codex/agents/bounded-worker.toml`](.codex/agents/bounded-worker.toml) 用于契约稳定、写集互斥的有界实现。
- [`.codex/agents/stage-reviewer.toml`](.codex/agents/stage-reviewer.toml) 用于高影响阶段的只读审查。

四个 profile 都是叶子角色；项目级 `[agents]` 设置 `max_depth = 1`，由宿主硬性阻止孙级 Agent。profile 中的升级约束是 defense in depth，范围不足时必须返回 escalation request，由主会话决定是否创建另一个独立叶子任务。

复杂跨模块任务可以由 `$agent-orchestration` 建立通用 `OrchestrationProgram`：主会话保留需求、问题模型、共享契约、调度、监督、集成、验收和交付，但不亲自承担委派切片的编码、测试、文档或审查工作；有界 workers 只处理互斥叶子切片，需要额外源码改动时由主会话重新派工。它不是“复杂任务一律多 Agent”，也不创建前端 / 后端专用模式；并行写入必须先满足阶段依赖、冻结相关跨切片契约并证明 write set 互斥，否则顺序 handoff。

这些 `.codex/` 文件只配置当前项目；仅安装 skill 不会修改其他项目或个人 Codex 配置。需要跨项目复用时，再显式复制到目标项目 `.codex/agents/` 或个人 `~/.codex/agents/`，并按 [OpenAI 官方 Codex subagents 文档](https://learn.chatgpt.com/docs/agent-configuration/subagents) 核对当前模型和配置字段。个人或项目根配置保持 `features.multi_agent = true` 与 `[agents].max_depth = 1`；不要只复制其中一半。验证时必须让承载会话的准确 runtime 完整解析配置并观察一次真实 spawn，同时确认叶子会话受宿主 max depth 限制；`codex --version`、profile 文件存在或只输出编排计划都不能证明已经生效。App / IDE 的内置 runtime 可能与终端 `PATH` 中的 `codex` 不同，需要分别检查。

## Optional Continuity Backends

`$task-continuity` 本身不安装状态服务。若宿主已有 task store、Trellis、memory、event index 或 lifecycle hooks，优先把它们映射为运行态 / reference backend。Codex 需要自动会话事件恢复时，可评估 [context-mode](https://github.com/mksglu/context-mode)；它已经实现 Codex `PreCompact` / `SessionStart`、SQLite/FTS5 和按需检索，避免重复建设数据库与 hook installer。它不提供复合源码指纹、reference cursor、证据 freshness 或 `first_allowed_action`，因此仍由 `$task-continuity` 负责是否可以继续执行。

若需要把“已验证 / 已接收 / 可提交 / 可发布”从模型声明提升为宿主门禁，可显式配置 [`task-continuity/scripts/codex_execution_adapter.py`](task-continuity/scripts/codex_execution_adapter.py)。它复用原生 hooks，自动记录少量 source / validation / delegation / delivery receipts，并在 source fingerprint 变化后让旧证据失效；stage / commit 不改变内容指纹，因此不会在交付时重复测试。源码写入只给代码索引置 dirty，实际选择图后端并发生真实查询时才刷新，避免每次 Bash 更新整图。运行态路径应位于宿主、Trellis 或其他不进入普通 Git 交付的位置；安装与配置见 [`task-continuity/references/host-adapters.md`](task-continuity/references/host-adapters.md)。

需要跨任务长期语义记忆时可单独评估 [MemPalace](https://github.com/MemPalace/mempalace)。第三方插件会新增本地数据、依赖、hook trust 和模型上下文，必须显式安装并做真实 compaction continuation 测试；MCP 已连接或快照出现不等于恢复有效。详细选择边界见 [`task-continuity/references/host-adapters.md`](task-continuity/references/host-adapters.md)。

## Install

### Option 1: Use CC Switch (Recommended)

如果你用 CC Switch 管理 Claude Code、Codex、Cursor 等工具的 skills / prompts，推荐直接将本仓库作为 skill repository 接入：

1. 在 CC Switch 中添加仓库：`https://github.com/jetlinks/jetlinks-develop-skills`
2. 以仓库根目录作为扫描入口，不要额外指定 `skills/` 子目录
3. 同步或启用需要的 skill，例如 `jetlinks-router`、`jetlinks-crud`、`jetlinks-events`、`jetlinks-web`
4. 刷新或重启目标工具，使新 skill 被重新发现

校验方式：

```text
使用 $jetlinks-router 分类当前 JetLinks 二开任务，并选择最少必要的 focused skills 落地。
```

### Option 2: Use Codex skill installer

如果当前环境带有 `$skill-installer`，可直接按仓库路径安装：

```text
Use $skill-installer to install skill from https://github.com/jetlinks/jetlinks-develop-skills/tree/master/jetlinks-router
```

也可以安装 focused skill，例如：

```text
Use $skill-installer to install skill from https://github.com/jetlinks/jetlinks-develop-skills/tree/master/jetlinks-reactive
```

或：

```text
Use $skill-installer to install skill from https://github.com/jetlinks/jetlinks-develop-skills/tree/master/jetlinks-web
```

也可以使用安装脚本：

```bash
python /path/to/install-skill-from-github.py \
  --repo jetlinks/jetlinks-develop-skills \
  --path jetlinks-router
```

### Option 3: Manual install

Codex 当前官方用户级目录为 `$HOME/.agents/skills`。若当前宿主已通过 `CODEX_HOME`、插件管理器或既有安装流程使用其他 skills root，沿用该已发现位置，不要同时复制同名 skill 到多个 root：

```bash
mkdir -p "$HOME/.agents/skills"
cp -R jetlinks-router "$HOME/.agents/skills/"
```

Codex 通常会自动发现 skill 变更；若未出现，再重启 Codex。

## Validate

仓库维护者在一个连贯修改阶段结束后统一运行：

```bash
python3 scripts/validate_skills.py
python3 -m unittest scripts/test_validate_skills.py
```

校验已安装镜像是否与仓库源完全一致时，显式传入宿主的镜像根目录：

```bash
python3 scripts/validate_skills.py --mirror-root /path/to/installed/skills
```

校验器检查技能包结构、frontmatter、UI metadata、本地引用、公开可执行资源与 Python 接口结构、四个通用技能的作者环境泄漏、可选 Codex 项目适配，以及镜像同步；它不假定 CC Switch、Trellis、Git 或某个固定安装位置，也不替代真实 prompt 的前向评测。

## Usage

从当前动作选择最少入口，已知 focused skill 时直接使用它。router 负责选择，领域技能负责实施；复杂求解准入、委派与恢复分别由对应通用技能拥有。跨层文件数或技术关键词不自动触发复杂流程。

已有目标、约束与实施授权在多轮中持续有效。进度提问或新提醒应融入原主线；压缩恢复只对账相关身份、已接受决定与保存的下一动作。读取是否更少、恢复是否更快都要由真实任务观察，不能仅凭文档短或离线测试通过宣称收益。

总入口调用：

```text
Use $jetlinks-router to classify this JetLinks scaffold task, choose the right focused skills, and implement the change.
```

Focused skill 示例：

- 使用 `$jetlinks-routing` 判断这个能力应该落在哪个模块。
- 使用 `$systematic-solving` 判断复杂求解准入，区分根因与证据有效性，并防止修复反复扩成局部特例；已明确的机械跨层任务沿领域路径实施。
- 使用 `$agent-orchestration` 判断真实委派收益并划分可独立负责的切片。选中多 Agent 后实际派发；总控负责规划、公共契约、协调与验收，实施、测试、文档和独立审查交给对应 owner，写集互斥。
- 使用 `$task-continuity` 保存原目标、持续约束、当前证据和唯一下一动作。实际恢复时核对必要身份；匹配后直接继续，失配时只对账相关范围。只有需要 Git / Trellis 映射时加载 JetLinks 恢复扩展。
- 使用 `$code-navigation` 先发现当前环境可用的检索能力，再从精确 symbol 或 changed items 出发，有界查询定义、引用、调用、组件 / 领域关系和候选测试；保留关系来源与置信度，不把语义相似度或作者机器上的工具当成精确事实或必需依赖。
- 使用 `$jetlinks-protocol` 分析协议包入口、编解码链路和二进制报文。
- 使用 `$jetlinks-crud` 为设备管理模块新增一个查询接口，并在自定义接口、复杂校验、权限边界或复杂查询处补必要代码注释。
- 使用 `$jetlinks-assets-permission` 判断一个 CRUD 或自定义查询接口是否需要 `AssetsHolder` 数据权限控制，并选择 `@AssetsController`、`AssetsHolderCrudController`、`CorrelatesAssetsHolderCrudController` 或 `AssetsHolder.injectQueryParam`；自定义权限边界必须在代码旁边说明。
- 使用 `$jetlinks-reactive` 优化当前 `Mono` / `Flux` 链路并避免阻塞；非显而易见的异步边界、批量 / 背压限制、上下文传播要补短注释。
- 使用 `$jetlinks-conventions` 判断复杂代码、公共类、SPI 方法应该如何写注释，以及是否需要 `@since` / `@see`；注释要求必须落到代码里，不能只写在回复或 PR 描述中。
- 使用 `$jetlinks-conventions` 判断关键业务链路是否需要 TraceHolder 埋点，并给出 span、属性和上下文传播方案。
- 使用 `$jetlinks-conventions` 判断常驻任务、缓存、队列或重试池是否需要 MBean，并给出统计、监控和运维操作方案。
- 使用 `$jetlinks-boundary` 判断该能力应该走直接依赖还是命令服务。
- 使用 `$jetlinks-events` 为现有模块增加订阅逻辑。
- 使用 `$jetlinks-web` 实现 Vue 页面、交互、组件与状态。局部字段、文案、样式或 props 修改走局部路径；新增页面或主要交互变化才建立方案，按相关导出复用组件，沿用 Ant Design 与本地 i18n。技术受众所需的 API / Topic 等内容可以准确展示。
- 使用 `$jetlinks-delivery` 起草中文 commit、生成 shell 提交命令、落实后端新增功能或行为变动的测试门禁、整理测试证据和 PR 描述。

## Prompt Templates

这些模板只表达诉求和决策，不指定 skill。智能体应根据本仓库规则自行判断使用哪些 skills、是否先设计、是否需要测试或交付门禁。

### 起手分析

```text
我正在考虑 <需求 / 想法>。
先帮我分析现状和相似实现，整理可选方案、风险点和需要我决策的问题。先不要开发。
```

### 功能设计

```text
我正在设计 <功能名> 功能。
请结合当前项目和可参考的平台做法，给出推荐方案、开发计划和需要我确认的问题。
```

### 后端能力

```text
我需要实现 <后端能力>。
先结合现有代码明确改变的行为和验证目标，按已明确需求直接实施；只有影响结果或权限的实质未决选择再问我。使用已有任务载体；无安全持久载体时保留有界上下文。长期结论有变化再原位同步权威文档。
```

### CRUD 管理能力

```text
我需要给 <业务对象> 增加管理能力，包含查询、详情、新增、修改、删除。
先看类似实现，分析数据权限和测试点，给我方案后再开发。
```

### 数据权限

```text
这个功能涉及 <业务对象 / 接口 / 查询结果> 的数据可见和操作范围。
先分析权限边界和当前项目的处理方式，拿不准的地方先问我。
```

### 前端页面

```text
我正在设计 <页面 / 功能> 页面。
请参考当前系统和其他平台的交互方式，先给页面结构、主要流程和实现计划；不要默认套表格页，后端枚举按 { value, text } 渲染。
```

### 复杂业务流程

```text
我正在做一个业务流程：<描述流程和目标>。
先分析涉及的模块、边界、事件、订阅和链路风险，给出方案和任务拆分。
```

### 反复失败止损

```text
这个问题已经尝试修过一次，但验收仍失败或失败转移到了同类场景。
请停止继续加条件、fallback、retry、mock 或兼容分支，重新列出已验证事实、被否定假设、竞争根因和最小区分检查；确认共同不变量和按实际行为变化选择的验证范围后再实现。
```

### 代码结构与影响面

```text
从 <入口 symbol / endpoint / changed paths> 出发，先用精确符号与构建事实确认 ownership，再只展开 1–2 跳调用 / 领域关系，区分确认边与推断边，给出影响消费者和候选测试；不要加载整张依赖图。
```

### 链路追踪

```text
我正在梳理 <功能 / 链路> 的可观测性。
先分析关键业务阶段、TraceHolder 埋点位置、关键信息和敏感信息边界，给出方案。
```

### 运维观测

```text
我正在设计 <常驻任务 / 缓存 / 队列>。
先分析是否需要 MBean，列出统计指标、监控字段和可安全执行的运维操作。
```

### 代码注释

```text
我正在整理 <模块 / 功能> 的代码可读性。
帮我检查哪些类、SPI 方法和复杂逻辑需要注释，必要时补 @since / @see，但避免逐行解释。
```

### Bug 定位

```text
这里有个问题：<现象描述>。
先帮我定位原因，不要急着改。请给出验证思路、修复方案和需要补的测试。
```

### 测试补齐

```text
我想给 <功能 / 改动点> 补测试，帮我先看一下应该怎么测。
先参考已有测试风格列出测试目标，确认后再补测试和运行验证。
```

### 继续开发

```text
采用你推荐的方案。
先做最小可用闭环，完成后告诉我改了什么、怎么验证、还有哪些风险。
```

### 方案调整

```text
这个方向需要调整：
- <调整点 1>
- <调整点 2>

请先更新任务契约和测试目标，再继续开发；不要把实时进度或失败流水追加到权威设计稿。
```

### 代码审查

```text
帮我审查当前改动。
重点看行为回归、权限遗漏、测试缺口、文档同步和 PR 风险。先列问题，再给建议。
```

### 交付和 PR

```text
这个需求已经开发完成，帮我整理交付并提交 PR。
先确认分支、目标 base、改动范围和测试结果，再提交 PR。
```

### 经验沉淀

```text
这次处理过程里好像有些经验可以复用，帮我判断一下是否值得沉淀。
如果值得，先告诉我建议沉淀成什么，等我确认后再写。
```

## Best Practices

完整实践见 [SECONDARY_DEVELOPMENT_PLAYBOOK.md](SECONDARY_DEVELOPMENT_PLAYBOOK.md)，涵盖：

- Claude Code / Codex / Cursor 的推荐协作方式
- 使用 CC Switch 安装本技能库的建议流程
- 简单 CRUD、复杂业务、测试修复等提示词模板与落地约束

## Git And PR Convention

JetLinks 项目交付代码时，默认遵循以下规范：

### Commit Title

- 提交标题优先对齐现有历史风格，采用 `type(scope): summary`。
- `type` 使用当前仓库已有语义，例如 `feat`、`fix`、`refactor`、`docs`、`test`。
- `scope` 使用受影响的业务域或模块名，例如 `基础模块`、`设备管理`、`prompt`。
- `summary` 使用简洁中文动宾短语，直接说明变更结果，避免空泛描述。

参考当前仓库已有风格：

- `refactor(prompt): 扩展低上下文边界决策规则`
- `refactor(基础模块): 优化菜单逻辑`
- `refactor(设备管理): 优化实体拓展型`

不建议：

- `update`
- `fix bug`
- `misc changes`
- 缺少 scope 的泛化标题，除非仓库历史本身就允许

### Branch Policy

- 禁止直接 push 到主干或集成分支，例如 `master`、`main`、`2.11`、`2.12`。
- 必须从目标基线分支拉出临时开发分支，再提交代码并发起 PR。
- 如果任务目标是发布到某个版本线，PR 的 base 必须明确指向对应版本分支。

推荐流程：

1. 从目标基线分支同步最新代码。
2. 创建临时分支实现需求或修复。
3. 按少量连贯阶段推进；提交已获授权时，在阶段完成并集中验证后创建本地 commit，不按步骤、文件或单个小修提交。
4. 阶段提交后更新任务运行态中的 Recovery Capsule；上下文压缩或恢复时先校验 task、Git 指纹和少量锚点，不重新全仓扫描。
5. 所有阶段和总体验收完成后，统一 push 临时分支并创建或更新一次 PR；PR 只写当前最终事实，不记阶段流水。
6. 通过 PR 合入目标版本分支。

### Testing And Delivery

后端契约、已有授权复用与按风险选测试由 [后端设计与测试规则](jetlinks-router/references/backend-design-test-driven-rules.md) 定义；提交与 PR 的团队规范由 [交付规则](jetlinks-delivery/references/git-and-pr-rules.md) 定义，README 不另列一套验收清单。

变化行为必须有有效证据。在连贯阶段结束后集中验证，相关输入未变化时复用结果；只有新变化、失败或证据失效才补跑。共享行为、安全边界、SQL 性能、TraceHolder、MBean、注释和 SPI 等仅按实际变化选择相应规则。已有仓库覆盖率门槛继续遵守，不为无门槛任务凑数字。

### Documentation Placement

[制品归属](jetlinks-router/references/document-placement-rules.md) 决定内容落点：README 和权威 docs 保留稳定当前事实；实时计划、失败、下一动作与胶囊留在已有 task / runtime，测试证据留在 PR / CI。无安全持久载体时使用有界 active context，不自动建立目录或修改 Git 忽略配置。恢复状态唯一由 [task-continuity](task-continuity/SKILL.md) 维护。

### PR Description

先说明触发问题与最终行为，再提供实际验证和真实风险。只加入本次涉及的设计、兼容、数据权限、公共契约、追踪或运维内容；已有明确实施授权无需补一张“用户确认状态”表。采用仓库实际模板时，省略未适用项或按其明确要求填写。

```md
## 变更
修复 / 新增的可观察行为，以及关键取舍。

## 验证
实际执行或复用的证据、覆盖行为与结果。

## 风险
真实未覆盖范围、兼容 / 发布影响，以及必要的文档同步。
```

仅在提交 / 发布已获授权时执行相应操作；任务整体完成后统一远程交付。需要提前共享或远端 CI 时沿授权维护同一个 draft，不按执行步骤创建 PR。使用 `gh` 时先使用当前可用权限，只有实际受限且动作已获授权时再走宿主审批机制。

## Skill Authoring Notes

- 新 skill 放在根目录的 `<skill-name>/`。描述只写能力与触发情形，入口保留执行所需最少规则；细节放已有 `references/` 并标明何时读取。
- 同一规则只设一个 owner；路由、领域调用方、README 示例与 UI metadata 引用它，不复制另一套准入、授权或恢复状态机。
- 指令细度与错误代价匹配。安全、授权、任务身份和证据真实性是实质约束；轮数、固定工具顺序、表格完整度和字数是诊断信息，不能单独证明完成或阻止已授权工作。
- 编辑后在一个连贯阶段统一检查结构 / 链接和受影响脚本测试，不按每次操作全量构建。结构检查不能证明智能体正确理解了指令。
- 维护触发、恢复或协作规则时，使用少量真实任务对照无该规则、当前规则与候选规则；保持模型、工具、源码和验收一致。检查目标保留、第一有效动作、遗漏 / 重问、任务偏航及所有智能体成本。只有观察到差异或不稳定时扩大样本，不给日常任务增加评测仪式。
- 至少覆盖明确机械跨层、已有协议样例修复、局部前端调整、复杂根因、依赖委派，以及匹配 / 失配恢复；把正确产出与效率分开判定，保留成功与失败轨迹供复审。
- 同一环境优先维护一个权威安装源。不要同时从多个技能根目录加载同名副本；同步镜像时用校验器明确比较，不自动修改用户安装或配置。

这些维护原则依据 [Agent Skills 规范](https://agentskills.io/specification)、[OpenAI 技能文档](https://learn.chatgpt.com/docs/build-skills)、[Anthropic 编写建议](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) 和 [Agent 评测指南](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)。文档是维护参考，不进入普通业务任务必读链。

## References

- OpenAI skills repository: https://github.com/openai/skills
- OpenAI curated skills layout: https://github.com/openai/skills/tree/main/skills
