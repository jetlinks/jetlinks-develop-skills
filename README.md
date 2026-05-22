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

### `jetlinks-protocol`

用于协议包开发、协议阅读、传输编解码、二进制报文分析和联调排障。

### `jetlinks-conventions`

用于共享编码规范、注解/导入确认、命名约束、i18n 判断与实现，以及 TraceHolder 链路追踪和 MBean 运维可观测性判断。

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

用于 JetLinks 前端页面开发、组件/hook/utils 能力复用、目录落点判断、状态管理与类型质量约束；坚持业务优先、参考为辅，默认沿用 Ant Design 风格；页面壳层、首屏组织、信息架构、视觉节奏或现有风格复用会受影响时，必须结合 `$jetlinks-web-style` 先完成页面风格选择或映射；需要交互打磨时，可结合 `$frontend-design`，但仍以当前前端框架风格为准，且最终界面必须面向终端用户而非开发者；用户可见字段展示名、标题、按钮和提示文案统一走国际化，可使用中文作为默认值。

### `jetlinks-web-style`

用于 JetLinks 前端页面风格选择与结构复用。当前端任务可能在标准管理表格页、筛选工作台式台账页、主从详情工作区、概览页、分步流、时间线、树表/分组管理等页面壳层之间选择，或用户要求参考/沿用某个现有页面风格时，先用它给出少量具体风格选项或直接映射既有风格，再交给 `$jetlinks-web` 实现。

### `jetlinks-capture`

用于任务结束后的知识沉淀判断、经验归档、playbook 生成，以及决定是否需要继续更新 prompt 或 skill。

### `jetlinks-delivery`

用于提交信息、提交命令、分支策略、后端设计与测试驱动门禁、测试证据和 PR 描述整理。

## Scenario Routing

推荐按场景直接使用 focused skill，不确定时再走总入口：

- 不确定该用哪个 skill：`$jetlinks-router`
- 只想处理协议包、编解码、认证或二进制报文：`$jetlinks-protocol`
- 只想确认代码规范、导入、i18n 判断、国际化实现、TraceHolder 埋点边界或 MBean 运维可观测性：`$jetlinks-conventions`
- 只想处理响应式链路：`$jetlinks-reactive`
- 只想找模块或新建模块：`$jetlinks-routing`
- 只想做 CRUD 或复杂查询：`$jetlinks-crud`
- 只想判断或实现 AssetsHolder 数据权限边界：`$jetlinks-assets-permission`
- 只想处理跨边界调用：`$jetlinks-boundary`
- 只想处理事件或订阅：`$jetlinks-events`
- 只想处理前端页面改造、能力复用、前端质量约束或在现有设计体系内优化交互：`$jetlinks-web`；若涉及页面壳层、首屏组织、信息架构或风格复用，同时用 `$jetlinks-web-style`
- 只想先选择或复用前端页面风格/页面壳层：`$jetlinks-web-style`
- 只想判断是否值得沉淀知识：`$jetlinks-capture`
- 只想整理提交、设计门禁、测试和 PR：`$jetlinks-delivery`

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

将目标 skill 目录复制到本地 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R jetlinks-router "${CODEX_HOME:-$HOME/.codex}/skills/"
```

安装完成后重启 Codex，使新 skill 被重新发现。

## Usage

总入口调用：

```text
Use $jetlinks-router to classify this JetLinks scaffold task, choose the right focused skills, and implement the change.
```

Focused skill 示例：

- 使用 `$jetlinks-routing` 判断这个能力应该落在哪个模块。
- 使用 `$jetlinks-protocol` 分析协议包入口、编解码链路和二进制报文。
- 使用 `$jetlinks-crud` 为设备管理模块新增一个查询接口。
- 使用 `$jetlinks-assets-permission` 判断一个 CRUD 或自定义查询接口是否需要 `AssetsHolder` 数据权限控制，并选择 `@AssetsController`、`AssetsHolderCrudController`、`CorrelatesAssetsHolderCrudController` 或 `AssetsHolder.injectQueryParam`。
- 使用 `$jetlinks-reactive` 优化当前 `Mono` / `Flux` 链路并避免阻塞。
- 使用 `$jetlinks-conventions` 判断关键业务链路是否需要 TraceHolder 埋点，并给出 span、属性和上下文传播方案。
- 使用 `$jetlinks-conventions` 判断常驻任务、缓存、队列或重试池是否需要 MBean，并给出统计、监控和运维操作方案。
- 使用 `$jetlinks-boundary` 判断该能力应该走直接依赖还是命令服务。
- 使用 `$jetlinks-events` 为现有模块增加订阅逻辑。
- 使用 `$jetlinks-web` 在前端改造中优先复用 `@jetlinks-web-core/@jetlinks-web` 组件、hooks、utils，并按目录/状态/类型约束落地；先分析真实业务目标，做到业务优先、参考为辅，不要默认套后台 CRUD；若页面壳层、首屏组织、信息架构、视觉节奏或现有风格复用会受影响，必须先结合 `$jetlinks-web-style` 选择或映射页面风格；视觉与组件语言默认沿用 Ant Design；如需交互或视觉优化，再结合 `$frontend-design`，但只能借鉴相似业务案例中真正适配的设计，且不要加入无意义的统计数字或装饰性数据块；用户可见字段展示名、列头、按钮与提示文案统一走 i18n，可用中文作默认值；线框图和设计说明只用于沟通，最终页面不要展示“交互方式”“设计原理”等开发者导向内容；若结构不确定，先问用户或先给线框图/效果图。
- 使用 `$jetlinks-web-style` 为前端页面先选页面壳层，例如 `标准管理表格页`、`筛选工作台式台账页`、`主从详情工作区`、`概览 / 工作台页`、`分步流 / 向导页`、`时间线 / 记录分析页` 或 `树表 / 分组管理页`，再交给 `$jetlinks-web` 实现。
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
先分析现有代码和影响范围；需要设计稿或测试目标时，先落档并等我确认，再开发。
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
请参考当前系统和其他平台的交互方式，先给页面结构、主要流程和实现计划。
```

### 复杂业务流程

```text
我正在做一个业务流程：<描述流程和目标>。
先分析涉及的模块、边界、事件、订阅和链路风险，给出方案和任务拆分。
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

请先更新设计稿和测试目标，再继续开发。
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
3. 完成测试后 push 临时分支。
4. 创建 PR 前先确认任务是否已完成：未完成用 draft，已完成再进入 review。
5. 通过 PR 合入目标版本分支。

### Testing Requirement

- 较大的后端改动或新功能必须先形成设计稿、任务拆分和测试目标，并落到当前工作区对应文档目录。
- 设计稿必须经过用户明确确认后才能进入开发；若实现过程中发现设计假设不成立，先更新设计稿并重新确认。
- 测试目标必须先于实现制定，映射真实使用场景和真实数据形态，而不是为了让测试通过而补形式化用例。
- 涉及 CRUD 查询、详情、更新、删除、批量操作、导出或自定义接口时，必须按 `$jetlinks-assets-permission` 分析是否需要 AssetsHolder 数据权限控制；资产类型、关联字段、权限动作、绑定关系或例外规则拿不准时先询问用户。
- 涉及关键后端业务链路、状态流转、命令执行、事件 / 订阅、协议链路、批处理或外部 I/O 时，必须说明 TraceHolder / MonoTracer / FluxTracer 埋点目标、关键属性、上下文传播和敏感信息排除；不新增埋点时说明已有平台自动追踪或不适用依据。
- 涉及常驻内存任务、缓存、队列、buffer、重试池、会话 / 连接 / 订阅管理器或后台执行器时，必须说明 MBean 运维可观测性决策、统计指标、监控字段、安全内部操作、生命周期和敏感信息排除；不新增 MBean 时说明已有覆盖或不适用依据。
- 本次提交必须经过相关单元测试，并按触发条件完成集成测试，至少覆盖本次改动涉及的核心路径。
- 后端新增功能或既有功能变动必须补充或更新对应单元测试，覆盖正常路径、关键异常路径和回归场景。
- 涉及数据库、消息、事件、协议联调、跨模块边界、外部依赖或启动装配时，PR 中必须提供集成测试结果；无法执行时只能作为阻塞或 draft 风险说明。
- 未触发集成测试条件时，PR 中必须写明不适用原因，不能留空。
- 如果仓库已配置覆盖率阈值，提交前必须满足阈值。
- 如果仓库没有统一阈值，也必须在 PR 中给出可验证的覆盖证据，而不是只写“已测试”。
- 不能提供测试结果、覆盖率结果或失败原因的提交，不应进入待合并状态。

### Documentation Placement

- README 只作为仓库或模块的长期总览，放定位、能力索引、入口说明和长期链接。
- 不要把单次任务过程、测试报告、PR 描述、临时计划、排查流水或总结放进 README。
- 较大功能的设计、方案取舍、任务拆分和测试目标，优先更新既有 design / plans / adr；没有归属时再新增一个主设计稿。
- 测试命令、覆盖率、集成测试结果等证据优先放 PR 描述或 CI 报告，不为每次运行新增测试报告文档。
- 经验沉淀先判断是否值得写；单次经验走 `.ai/`，稳定通用后再考虑回写 prompt 或 skill。
- 同一主题优先维护一个主文档，避免拆出多个 plan、summary、test-report、worklog 碎片。

PR 中至少应提供这些数据：

- 执行过的测试命令
- 较大后端改动或新功能的设计稿路径、用户确认状态和测试目标达成情况
- 新增或更新的测试类和核心覆盖点
- 测试类型：单元测试、集成测试、端到端测试中的哪些
- 通过数量、失败数量、跳过数量
- 覆盖率数据，例如 line、branch、changed files 或 changed classes 的覆盖结果
- 若存在限制或未覆盖项，明确列出风险边界

### PR Description

PR 描述必须聚焦事实和结果，至少包含：

- 目的：为什么要做这次改动
- 核心变动：改了哪些模块、行为和边界
- 设计与测试目标：较大后端改动或新功能需列出设计稿路径、确认状态、测试目标达成情况、CRUD / AssetsHolder 数据权限分析结论、链路追踪结论和 MBean 运维可观测性结论
- 测试结果：命令、新增或更新的测试类、通过数、失败数、跳过数、覆盖率数据、集成测试结果或不适用原因
- 文档同步情况：已同步哪些原始文档，或说明无需同步的原因
- 兼容性与发布边界：说明是否为 PR 内未发布逻辑收敛；已发布、持久化或外部依赖的变更需写清兼容或迁移策略
- 数据库兼容与 SQL 性能：涉及复杂 SQL / 原生 SQL 时说明标准 SQL、方言范围、索引 / 分页风险和压测结果
- 风险与影响面：哪些场景受影响，哪些场景未覆盖

推荐模板：

```md
## 目的

- 修复 / 优化 / 新增什么能力
- 解决了什么问题

## 核心变动

- 模块 A：做了什么调整
- 模块 B：新增了什么约束或行为

## 设计与测试目标

- 设计稿：`docs/plans/yyyy-mm-dd-xxx.md`
- 用户确认：已确认 / 未确认，当前为 draft
- 测试目标：真实场景、真实数据、正常路径、异常路径、回归路径和边界路径均已覆盖 / 列出未覆盖原因
- 数据权限：适用 / 不适用；适用时说明 `AssetType`、`CrudAssetPermission`、查询注入、操作校验和关联资产边界
- 数据库兼容与性能：适用 / 不适用；适用时说明标准 SQL / 方言范围、索引与分页风险、压测结果或替代验证
- 链路追踪：适用 / 不适用；适用时说明 TraceHolder / MonoTracer / FluxTracer 埋点位置、关键属性、上下文传播和敏感信息排除
- MBean 运维可观测性：适用 / 不适用；适用时说明 MBean 名称、统计指标、运维操作、生命周期和敏感信息排除

## 测试结果

- 命令：`mvn -pl xxx -am test`
- 新增/更新测试：`XxxServiceTest` 覆盖新增规则、异常分支和回归场景
- 单元测试：42 passed, 0 failed, 1 skipped
- 集成测试：8 passed, 0 failed / 不适用：未涉及数据库、消息、事件、协议、跨模块边界、外部依赖或启动装配
- 压力测试：适用 / 不适用；适用时给出数据规模、并发数、耗时阈值和结果
- 覆盖率：line 81.4%, branch 73.2%

## 文档同步情况

- 已同步：模块 README / API 文档 / 设计稿 / ADR / AGENTS 等长期归属文档
- 未同步：无 / 说明原因
- 说明：README 仅在长期总览需要变化时更新；测试证据放 PR / CI

## 风险与说明

- 影响范围：
- 兼容性与发布边界：
- 数据库兼容与 SQL 性能：
- 链路追踪 / 可观测性：
- MBean / 运维可观测性：
- 未覆盖场景：
- 回滚方式：
```

结论要求：

- 用数据说话，不要只写“测试通过”
- 没有覆盖率数据时，至少说明为什么缺失，以及提供了哪些替代证据
- 创建 PR 前先确认任务是否已完成：未完成使用 draft PR，已完成且用户确认后再 ready for review
- 默认不要在一个 PR 中提交大量代码，优先按清晰主题拆分
- 如果仓库远端是 GitHub，默认优先使用 `gh pr create` 创建 PR
- 如果当前工具支持非沙箱审批或提权机制，`gh` 命令应申请非沙箱执行；不支持时说明限制并降级处理
- 没有 PR 的直推提交流程，视为不符合规范
- 仓库默认模板见 `.github/pull_request_template.md`

## Skill Authoring Notes

为保证该仓库可持续扩展，新增 skill 时遵循这些规则：

- 新 skill 放在仓库根目录的 `<skill-name>/` 下。
- `SKILL.md` 只保留触发描述和执行流程，不放仓库级使用文档。
- 详细规则、索引和参考资料放入 `references/`。
- 需要 UI 元数据时，在 `agents/openai.yaml` 中维护。
- 新增或调整 skill 后，运行：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  <skill-name>
```

## References

- OpenAI skills repository: https://github.com/openai/skills
- OpenAI curated skills layout: https://github.com/openai/skills/tree/main/skills
