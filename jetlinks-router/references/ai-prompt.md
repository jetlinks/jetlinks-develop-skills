# JetLinks AI 开发规则索引

本文件是 JetLinks 系脚手架的总路由，用来帮助智能体先判断任务类型，再切换到最合适的 focused skill，最后按当前工作区的真实实现落地。

**上下文**：本文件较长；日常可先读 `../agents/openai.yaml` 的默认提示词，再按需打开本文件的对应章节。前端交互细则在 `jetlinks-web-style` 分片（`style-catalog-core-base.md` / `style-catalog-core-detail-shell.md` / `style-catalog-templates.md` 等），不要在 router 内复制前端规则正文。

它不提供仓库快照，不硬编码模块清单、包名、版本号或固定目录结构。所有这类信息都必须从当前工作区现有代码、`pom.xml`、资源目录和相邻模块中发现。

## 全局原则

1. 先发现，再实现
    - 不凭记忆假设模块名、注解包、依赖坐标、命令 ID、Topic、资源路径。
    - 先查看当前工作区的相邻代码、父子模块结构、现有配置和示例。
    - 结构检索先定义问题，并用 `$code-navigation` 发现当前环境可用能力，再走“已有锚点 → 精确事实 → 符号语义 → 有界结构关系 → JetLinks 领域扩展 → 深层 / runtime 证据”的漏斗；不预设 Git、`rg`、LSP、图数据库或 MCP，向量相似度和推断调用边只能发现候选。

2. 复杂任务先 plan 再实施
    - 对跨模块、多子任务、需求仍在变化、存在多个方案或兼容性风险的任务，先输出精简计划并等待用户确认。
    - 计划至少包含目标、范围、不做什么、实施步骤、风险 / 待确认点和验证方式。
    - 简单低风险小任务可在给出简短计划后直接实施。
    - 计划只描述怎么推进，不能替代问题模型。复杂 / 高不确定任务还必须切通用 `$systematic-solving` 并加载 [`systematic-solving-jetlinks-rules.md`](systematic-solving-jetlinks-rules.md)，明确可观察目标、不变量、变化轴、竞争假设、区分证据、局部修补预算和验证矩阵，再映射到 JetLinks 制品与交付。
    - 同一根因假设的一次实现仍未通过验收、失败转移到同类场景，或下一步准备新增场景判断 / fallback / retry / mock / 兼容分支时，立即停止编辑并重构假设；不要在原计划下面继续追加微补丁。
    - 实时计划与长任务连续性切通用 [`$task-continuity`](../../task-continuity/SKILL.md)，把计划维护成当前状态投影：阶段切换时替换已失效步骤并压缩为当前阶段、剩余事项、有效假设、下一步和阻塞，不逐轮追加完成项或阶段总结。
    - JetLinks 工作区再按 [`context-recovery-rules.md`](context-recovery-rules.md) 将通用 Recovery Capsule 映射到 task ID / revision、branch / HEAD、changed paths。上下文压缩或恢复后只读胶囊列出的 3–7 个锚点；指纹一致时禁止重新全仓扫描。

3. 后端大改先设计与测试目标，再开发
    - 对较大的后端改动或新功能，必须遵循 [`backend-design-test-driven-rules.md`](backend-design-test-driven-rules.md)。
    - 文档落点遵循 [`document-placement-rules.md`](document-placement-rules.md)：README 只放长期总览，测试报告、任务流水和 PR 证据不放 README。
    - 待确认设计先写 Trellis active task；无 Trellis 时写经 `git check-ignore -v` 验证的单一运行态文件，再等待用户明确确认，不先污染受 Git 管理的 `docs`。
    - 用户确认后，只有长期需求、稳定契约、架构 / API / 模块设计、验收语义或长期风险变化时，才原位更新权威 docs；删除过时描述，不追加“本轮总结”“完成情况”或时间线。
    - 实时任务拆分、checkbox、假设账本、步骤进度、调试尝试、失败轨迹、临时下一步、测试日志、PR 文案或会话总结留在任务运行态，不进入权威文档。
    - 用户确认后，先按真实使用场景和数据制定测试目标，再实现代码，直到测试目标达成。
    - 不允许为了让测试通过而删除测试、弱化断言、只跑无关测试、改低业务期望或绕过真实校验。
    - 兼容性是通用发布边界判断，不只限于 CRUD：API / DTO / Event / Topic / Command / 协议 / 配置 / 前端路由 / QueryParam / termType 等同一 PR 内未发布中间形态优先收敛到最佳实践；已合入、已发布、已有持久化数据或外部依赖时才设计兼容 / 迁移。
    - 添加兼容代码前必须说明兼容对象；拿不准是否已发布或外部依赖时，只问一个具体确认问题，不为了保险保留旧分支。

4. 只切换必要 skill
    - 本文件只做路由。
    - 进入某个场景后，只加载最少数量的 focused skill。

5. 优先复用现有抽象
    - JetLinks 系项目通常已经提供 CRUD 基类、命令服务、事件、订阅、国际化约定。
    - 默认沿用现有模式，不新增平行方案。
    - 对集合、Map、数组和对象判空以及常见默认值处理，在依赖已存在或相邻实现已使用时，优先复用 Apache Commons 工具类，不手写重复判空模板；不要把 `org.apache.commons.lang3.StringUtils` 整类视为禁用。字符串比较 / 前后缀 / 包含 / 索引 / 普通替换等已废弃 Commons Lang 操作按大小写语义必须用 `Strings.CS` / `Strings.CI`；`StringUtils.isEmpty` / `isBlank` 等未废弃 null-safe predicate 可按模块 Commons Lang 风格使用，具体规则切到 `$jetlinks-conventions`。

6. 以当前模块风格为准
    - 响应式或阻塞式、`javax` 或 `jakarta`、控制器基类、服务基类、i18n 路径，都以目标模块现状为准。
    - 仅在新建模块且没有可参考实现时，才基于通用规则做最小决策。
    - 前端任务也以当前 workspace 为准：先路由到 `$jetlinks-web`；除局部调整白名单外，同时组合 `$jetlinks-web-style` 建立页面交互方案档案。
    - 前端通用组件、hooks、utils 以当前 workspace 的 `jetlinks-web-core` 和相邻页面真实用法为准；详细前端约束不在 router 中重复维护。

7. 生成最小可用实现
    - 只实现用户明确要求的内容。
    - 不额外生成示例实体、演示接口、假设性的扩展点。
    - 保持改动范围聚焦，不把无关重构、顺手修复或跨主题整理混进当前任务。
    - 涉及 CRUD 查询、详情、更新、删除、批量操作、导出或自定义接口时，必须分析是否需要 AssetsHolder 数据权限控制；具体实现切到 `$jetlinks-assets-permission`，不要手写租户 / 部门 / 创建人过滤替代统一资产权限；资产类型、关联字段、权限动作或例外规则拿不准时先询问用户。

8. 软链接模块同样属于工作区事实
    - 如果模块、组件或聚合目录是符号链接，不要忽略。
    - 需要同时识别“链接入口路径”和“真实目标路径”，必要时沿链接继续读取代码与配置。

9. 低上下文脚手架也要可工作
    - 如果当前仓库几乎没有业务代码、只有少量模板或只是空脚手架，不要停在“缺少参考实现”。
    - 在这种情况下，允许退化到“模板仓库模式”：基于根 `pom.xml`、目录结构、已有依赖和本规则集生成最小可用骨架。
    - 退化模式不仅适用于模块创建，也适用于 CRUD、权限、命令边界、事件驱动和基础 i18n 决策。

10. 任务结束时可以判断是否值得沉淀知识
    - 只有产出了稳定、跨任务可复用、非显然的知识时，才建议沉淀；任务完成或需要总结本身不是创建 worklog 的理由。
    - 优先原位更新已有权威来源、项目规范或 skill；只有缺少归属且确有长期价值时才新增 knowledge / playbook。
    - 单次过程流水留在 Trellis / 本地运行态，测试证据留在 PR / CI；不把它们转换成可提交的总结文档。
    - 不为每次任务默认新增文档；先更新已有归属文档，或把一次性测试证据留在 PR / CI。
    - 如果判断值得沉淀，不要直接结束任务；应先提示用户是否需要生成正式文档。
    - 如果结论已经成熟到可抽成通用 JetLinks skill，还应额外询问是否并入 `jetlinks-develop-skills` 并准备官方 PR。

11. 一个任务可以同时使用多个 focused skill
    - 例如“新建模块并补 CRUD”通常会同时使用模块路由、通用规范和 CRUD skill。
    - 例如“改事件处理器并整理 PR”通常会同时使用事件订阅、响应式实践和 Git 交付 skill。
    - 例如“改前端列表页并补提交流程”通常会同时使用前端 skill 和交付 skill。

12. 用户可见异常默认属于 i18n 范畴
   - 优先沿用当前模块已有的 `i18nCode` / message key 异常模型，不在异常构造里写死 message。
   - 只有本地异常体系确实只支持 `message` 时，才在边界层回退到本地化后的文本。

13. 根因优先，禁用奇技淫巧：统一以 [`jetlinks-conventions/references/root-cause-and-no-hack-rules.md`](../../jetlinks-conventions/references/root-cause-and-no-hack-rules.md) 为准；router 不重复列举禁止清单。
    - 上述文件负责实现红线；复杂问题的动态求解、失败止损和假设重构统一由 [`$systematic-solving`](../../systematic-solving/SKILL.md) 负责，JetLinks 制品与领域映射由 [`systematic-solving-jetlinks-rules.md`](systematic-solving-jetlinks-rules.md) 补充。

14. 注释要平衡人类可读性和模型上下文
   - 复杂业务规则、兼容逻辑、并发 / 生命周期保护、安全边界、TraceHolder / MBean 决策等，需要结合 [`jetlinks-conventions/references/code-comments.md`](../../jetlinks-conventions/references/code-comments.md) 写短注释。
   - 类注释和 SPI 接口方法注释必须完整，写清职责、调用时机、参数、返回、错误、副作用和实现约束；必要时补真实 `@since` 和指向订阅相关类型 / 参考实现的 `@see`。
   - 简单赋值、DTO 搬运、直观方法调用不写噪声注释；优先用好命名和小方法，注释只解释原因和边界。
   - 注释要求必须落到代码里；最终回复、设计稿或 PR 说明不能替代代码旁边的类注释、方法注释或关键分支短注释。

15. 常驻能力要考虑运维可观测性
   - 涉及常驻内存任务、缓存、队列、buffer、重试池、会话 / 连接 / 订阅管理器或后台执行器时，必须结合 [`jetlinks-conventions/references/mbean-observability.md`](../../jetlinks-conventions/references/mbean-observability.md) 判断是否需要 MBean。
   - 目标是辅助运维快速定位问题：看统计、看状态、看最近错误，并在安全边界内刷新缓存、flush、compact 或手动重试。

## 标准工作流

1. 分类任务
    - 判断这是结构发现、模块创建、CRUD、复杂查询、跨服务调用、实时订阅、事件驱动、国际化、前端页面改造、代码注释、MBean 运维可观测性还是导入/注解确认。

2. 判断是否进入 `plan-first`
    - 如果任务复杂、跨模块、需求仍在变化、涉及多个子任务，或存在多个方案 / 明显风险，先输出计划并等待用户确认。
    - 如果是较大的后端改动或新功能，先读取 [`backend-design-test-driven-rules.md`](backend-design-test-driven-rules.md) 和 [`document-placement-rules.md`](document-placement-rules.md)；有 `.trellis/` 再读 [`trellis-integration-rules.md`](trellis-integration-rules.md)。把待确认设计和测试目标落到任务运行态，等待用户确认后才能实现，再按需提升稳定结论到权威 docs。

3. 判断是否进入系统性求解
    - 复杂、高不确定、跨边界、候选根因不唯一的任务，组合 [`$systematic-solving`](../../systematic-solving/SKILL.md) 与 [`systematic-solving-jetlinks-rules.md`](systematic-solving-jetlinks-rules.md)。
    - 任务即使起初简单，只要一次实现仍未通过验收、失败转移、继续需要特例 / fallback / retry / mock / 兼容分支，或连续操作没有得到新证据，也立即切入。
    - 先冻结任务契约，建立完整执行路径、竞争假设、区分检查、解法层级和验证矩阵，再允许生产代码编辑。

4. 检索当前工作区
    - 若已有 Recovery Capsule 或精确 symbol / changed path，先用 `$task-continuity` 核对身份和指纹，再从锚点开始，不重新全仓扫描。
    - 否则先查看当前工作区实际存在的根目录、构建 / 包配置、聚合模块、资源目录和链接边界，再使用 [`$code-navigation`](../../code-navigation/SKILL.md) 定向查 ownership、引用 / 调用和影响面；涉及 JetLinks 领域流时再读 [`code-navigation-jetlinks-rules.md`](code-navigation-jetlinks-rules.md)。
    - 结构图只返回有界路径、文件 / symbol 锚点、revision、证据来源和置信度；高影响推断边必须回到源码、构建或运行时证据确认。

5. 切换最少 skill
    - 只切到覆盖当前任务的 focused skill。

6. 找相邻示例
    - 在目标模块或相似模块中定位同类实现。
    - 如果示例位于软链接模块中，允许沿链接读取其真实内容。
    - 如果没有相邻示例，切换到模板仓库模式，按通用规则生成最小实现。

7. 实现
    - 复用现有抽象，保持命名、分层、注解和返回类型一致。

8. 校验
    - 检查依赖、注解、导入、编程模型、权限、i18n、事件或 Topic 是否与当前工作区一致。
    - 如果当前环境无法直接执行验证，也要明确给出待执行命令、预期验证点和剩余风险边界。

9. 交付
    - 如果任务包含提交、推送或发 PR，切换到 `$jetlinks-delivery`。
    - 后端新增功能或既有功能变动必须先补或更新对应单元测试。
    - 较大后端改动或新功能的交付说明必须引用任务契约路径、用户确认状态、权威文档同步结论和测试目标达成情况。
    - 运行改单涉及的单元测试；涉及数据库、消息、协议、跨模块边界、外部依赖、启动装配或事件链路时再跑集成测试，未触发时写明不适用原因。
    - 输出测试命令、通过数、失败数、跳过数和覆盖率数据。
    - 每个有独立验收信号的连贯阶段完成并验证后，先创建一个本地 commit，再用实际 commit hash 和下一步刷新恢复胶囊；不要为每个操作、文件或小步骤提交。
    - 所有阶段和总体验收矩阵完成后，才统一 push 分支并创建或更新一次 PR。未获用户明确要求时，不为中间步骤创建 draft PR，也不把 PR 描述 / 评论当进度流水。

10. 沉淀
    - 如果任务已经完成，且产出了稳定经验，切换到 `$jetlinks-capture`。
    - 先判断值不值得沉淀；默认不把单次任务总结写成 worklog，优先回写已有 canonical knowledge / playbook / skill。
    - 先给出沉淀建议、推荐路径和摘要草稿；用户确认后再生成正式文档。
    - 如果结论已具备跨项目复用价值，再询问是否并入 `https://github.com/jetlinks/jetlinks-develop-skills` 并准备 PR。

## 任务路由

### 复杂、高难度或反复失败的问题

切换：
- [`$systematic-solving`](../../systematic-solving/SKILL.md) + [`JetLinks 系统性求解扩展`](systematic-solving-jetlinks-rules.md)
- [`$task-continuity`](../../task-continuity/SKILL.md) + [`JetLinks 上下文恢复适配`](context-recovery-rules.md)
- 再组合承担具体实现的领域 skill

适用：
- 跨多个模块、层次或同步 / 异步边界才能理解完整行为
- 涉及并发、生命周期、兼容、性能、权限、状态一致性或多种实现变体
- 同一验收信号在一次实现后仍失败，或失败转移到同类输入 / 相邻实现
- 下一步准备继续增加特例、fallback、retry、mock、兼容别名、隐藏开关或复制实现
- 连续搜索、构建或操作没有产生能区分候选根因的新证据

边界：
- 该 skill 管问题模型、停滞门禁、解法层级和验证矩阵；CRUD、协议、响应式、前端等细节仍由对应领域 skill 管理。
- 根因明确且不影响共享契约的导入、语法、格式或单点机械修复不强制进入。

### 先看哪些模块、能力和目录

切换：
- [`$jetlinks-routing`](../../jetlinks-routing/SKILL.md)

适用：
- 不知道代码应该落在哪个模块
- 不知道当前脚手架有哪些业务域、组件域、聚合模块
- 不确定新功能应该挂到现有模块还是新建模块

### 判断“直接依赖 / 命令调用 / 事件 / 订阅”

切换：
- [`$jetlinks-boundary`](../../jetlinks-boundary/SKILL.md)
- [`$jetlinks-assets-permission`](../../jetlinks-assets-permission/SKILL.md)

适用：
- 需要使用其他模块能力
- 不确定是加 Maven 依赖、调用命令服务、发布事件还是订阅消息
- 需要判断命令调用应优先复用显式 command 对象，还是只是跟随本地快捷 API
- 空脚手架中首次建立模块边界约定

### 协议包 / 编解码 / 二进制报文

切换：
- [`$jetlinks-protocol`](../../jetlinks-protocol/SKILL.md)

适用：
- 需要修改 `ProtocolSupportProvider`、`DeviceMessageCodec`、传输路由或认证流程
- 需要分析 MQTT、HTTP、TCP、UDP、CoAP 等协议接入方式
- 需要阅读或调整二进制报文、ACK、消息序号或属性和功能消息映射

### 确认注解、包名、导入

切换：
- [`$jetlinks-conventions`](../../jetlinks-conventions/SKILL.md)

适用：
- 不确定 `javax`/`jakarta`
- 不确定实体、控制器、事件、命令、订阅的注解和导入
- 需要判断复杂代码是否应该补注释，以及类注释 / SPI 方法注释是否完整，SPI 是否需要 `@since` / `@see`
- 需要为常驻任务、缓存、队列或重试池判断 MBean 运维可观测性边界

### 创建新模块或聚合模块

切换：
- [`$jetlinks-routing`](../../jetlinks-routing/SKILL.md)

适用：
- 新建 manager/core/adapter 模块
- 调整聚合 `pom.xml`、自动配置、资源目录
- 空脚手架中首次创建业务模块

边界：
- 如果存在 `manager` / `core` 分层，CRUD、Controller、应用 Service、持久化 Entity / Repository、权限校验、i18n 和运行时装配归 `manager`。
- `core` 只承载公共 domain、DTO、命令 / 事件定义、常量、SPI / 扩展接口等跨模块契约。
- 不因“需要 CRUD”“存在 DTO”“以后可能复用”把 CRUD 放进 `core`，也不默认创建 `xxx-api`。

### 代码结构 / 调用链 / 变更影响检索

切换：
- [`$code-navigation`](../../code-navigation/SKILL.md)
- JetLinks 领域关系按需读取 [`code-navigation-jetlinks-rules.md`](code-navigation-jetlinks-rules.md)

适用：
- 查 definition / references / implementations / type hierarchy / callers / callees
- 梳理 Maven 模块依赖、跨层生产者—边界—消费者路径
- 追踪 Command / Event / Topic / AssetsHolder / Protocol / Vue route-API 领域关系
- 根据 changed paths 识别影响面、同类实现和候选测试
- 为复杂任务或上下文恢复建立少量可验证锚点

边界：
- 精确事实优先；语义检索只给候选。
- 不一次加载整张图，默认从一个入口 1–2 hop 展开。
- 动态分派、Spring 代理 / 反射、事件 Topic 和 Vue runtime registration 保留置信度并按需用运行时证据复核。

### 标准 CRUD

切换：
- [`$jetlinks-crud`](../../jetlinks-crud/SKILL.md)

适用：
- Entity / Service / Controller 的常规新增或修改
- 标准增删改查
- 权限、校验、基础 i18n
- AssetsHolder 数据权限可见范围、详情访问、更新删除校验、批量操作和导出边界判断
- 空脚手架中首次创建基础 CRUD 骨架；若存在 `manager` / `core` 分层，CRUD 骨架落到 `manager`，公共 DTO / 命令契约才落到 `core`

### 复杂 CRUD / 查询 / 批处理

切换：
- [`$jetlinks-crud`](../../jetlinks-crud/SKILL.md)

适用：
- 复杂条件查询、分页、聚合、批量修改、关系同步
- CRUD 伴随复杂副作用
- 关联查询或跨模块查询需要判断 AssetsHolder 权限作用在实体自身、关联资产还是服务边界

### 数据权限 / 资产权限

切换：
- [`$jetlinks-assets-permission`](../../jetlinks-assets-permission/SKILL.md)

适用：
- CRUD、自定义查询、聚合、导出、详情、更新、删除、批量操作需要数据权限控制
- 需要判断 `AssetType`、`@AssetsController`、`AssetsHolderCrudController`、`CorrelatesAssetsHolderCrudController`、`CrudAssetPermission`
- 需要使用 `AssetsHolder.injectQueryParam`、`AssetsHolder.assertPermission`、`AssetsHolder.filterAssets`
- 命令服务、订阅或消息推送需要按资产权限过滤
- 拿不准资产类型、关联字段、权限动作或绑定关系

### 跨服务或跨边界调用

切换：
- [`$jetlinks-boundary`](../../jetlinks-boundary/SKILL.md)

适用：
- 命令服务
- 服务代理
- 远程查询和远程操作
- `commandSupport.execute(QueryCommand.of(...))` 这类显式命令对象优先级判断

### 实时消息 / Topic 订阅

切换：
- [`$jetlinks-events`](../../jetlinks-events/SKILL.md)

适用：
- `@Subscribe`
- EventBus/Topic 流式处理
- 设备消息、系统消息、广播消息

### 领域事件 / 生命周期事件

切换：
- [`$jetlinks-events`](../../jetlinks-events/SKILL.md)

适用：
- `@EventListener`
- 实体新增、修改、删除后的副作用
- 事务提交后的异步处理

### 国际化

切换：
- [`$jetlinks-conventions`](../../jetlinks-conventions/SKILL.md)

适用：
- 新增枚举、实体字段、权限、操作、错误消息、提示消息
- 需要把用户可见异常改成 `i18nCode` / message key，而不是写死 message
- 需要判断当前模块是否应该补 i18n
- 需要处理 `LocaleUtils`、`I18nEnumDict`、`messages_zh/messages_en` 等实现细节

### 前端页面开发与改造

切换：
- [`$jetlinks-web`](../../jetlinks-web/SKILL.md)
- 除局部调整白名单外，组合 [`$jetlinks-web-style`](../../jetlinks-web-style/SKILL.md) 先建立方案档案；结构不确定时再让用户选择
- 如任务明确包含页面美化、交互优化、信息层级梳理或状态反馈打磨，在抽取本地样式锚点后再结合 `$frontend-design`

适用：
- Vue3 页面、弹窗、列表、详情改造
- 需要复用当前 workspace 的 `jetlinks-web-core` / `@jetlinks-web` 组件、hooks、utils
- 需要判断前端目录落点、状态边界、类型与质量约束
- 需要先分析业务目标，再决定交互方案，而不是默认 CRUD 表格页
- 多方案时让用户选择业务交互方案；组件落地仍以 `jetlinks-web-core` 真实导出、组件实现和相邻页面用法为准
- `jetlinks-project-ui-cli` 只在用户明确要求时作为外部参考，不是默认依赖或导入来源
- 需要前端 i18n、后端 `EnumDict` / `I18nEnumDict` 的 `{ value, text }` 渲染、ConditionFilter 优先级、轻量字段编辑、无意义数据规避或原型标注清理等细则时，直接遵循 `$jetlinks-web`
- 标准管理表格页不是信息不足时的兜底；`ProSearch` 必须有窄改旧页、用户明确要求旧表格风格或轻量固定筛选的例外理由

### 知识沉淀与经验归档

切换：
- [`$jetlinks-capture`](../../jetlinks-capture/SKILL.md)

适用：
- 任务已经完成，需要判断是否产生了跨任务稳定知识
- 需要判断应原位更新哪个 canonical 来源，或是否确有必要新增 knowledge / playbook
- 需要区分任务运行态、PR / CI 证据和长期知识，避免把过程总结固化成仓库文档
- 需要判断这次结论是否已经可以抽成 skill，并继续提交到官方 skills 仓库

### 提交、分支、PR 与测试交付

切换：
- [`$jetlinks-delivery`](../../jetlinks-delivery/SKILL.md)

适用：
- 需要 commit、push、发起 PR
- 需要起草或审查中文 commit message
- 需要生成 shell 可执行的 git commit 命令
- 需要整理提交信息、PR 标题或 PR 描述
- 需要确认是否允许直接推送到目标分支
- 需要给出测试和覆盖率证明
- PR 包含后端新增功能或既有功能变动，需要补齐单元测试、覆盖率、集成测试结果或不适用原因

## 常见组合

- 复杂任务或一次修复后仍失败
    - `$systematic-solving`
    - 任务较长、需要恢复或分阶段交付时加 `$task-continuity`
    - 加入与真实执行路径匹配的 `$jetlinks-crud` / `$jetlinks-boundary` / `$jetlinks-events` / `$jetlinks-reactive` / `$jetlinks-protocol` / `$jetlinks-web`
    - 公共能力和 no-hack 红线再加 `$jetlinks-conventions`

- 新建模块并提供 CRUD
    - `$jetlinks-routing`
    - `$jetlinks-crud`
    - `$jetlinks-conventions`

- 在现有模块补一个查询接口
    - `$jetlinks-routing`
    - `$jetlinks-crud`
    - 如模块是响应式，再加 `$jetlinks-reactive`

- 调用其他模块能力
    - `$jetlinks-boundary`
    - 如是响应式模块，再加 `$jetlinks-reactive`

- 修改协议包或联调设备接入
    - `$jetlinks-protocol`
    - 如涉及提交与测试证据，再加 `$jetlinks-delivery`

- CRUD 后要同步其他数据
    - `$jetlinks-crud`
    - `$jetlinks-events`
    - 如涉及响应式链路，再加 `$jetlinks-reactive`

- 常驻缓存、重试队列或后台任务
    - `$jetlinks-conventions`
    - 如涉及事件 / 订阅消费，再加 `$jetlinks-events`
    - 如涉及响应式链路，再加 `$jetlinks-reactive`

- 处理设备或系统消息流
    - `$jetlinks-events`
    - 如需要持久化或反查实体，再加 `$jetlinks-crud`

- 前端页面改造并保持能力复用
    - `$jetlinks-web`
    - 除局部调整白名单外，同时加 `$jetlinks-web-style` 先建立方案档案
    - 如命名/导入/i18n 有约束，再加 `$jetlinks-conventions`

- 前端页面交互优化并保持当前框架风格
    - `$jetlinks-web`
    - `$frontend-design`
    - 如命名/导入/i18n 有约束，再加 `$jetlinks-conventions`

- 前端页面业务流复杂且结构未定
    - `$jetlinks-web`
    - `$jetlinks-web-style`
    - 先建立业务交互方案档案；事实清楚时默认采用推荐方案，结构不确定时让用户在少量方案中选择；必要时先输出线框图或效果草图，再进入实现

- 前端页面需要参考相似业务并统一 Ant Design 风格
    - `$jetlinks-web`
    - 除局部调整白名单外加 `$jetlinks-web-style`
    - `$frontend-design`
    - 参考案例只辅助业务方案和交互节奏，组件仍以当前 workspace 的 `jetlinks-web-core` 为准

- 提交并发起 PR
    - `$task-continuity`
    - `$jetlinks-delivery`
    - 如改动涉及具体模块，再加对应业务 skill

- 复杂问题需要先建立调用链和影响面
    - `$code-navigation`
    - `$systematic-solving`
    - 长任务再加 `$task-continuity`
    - 再按 owning module 加对应领域 skill

- 任务完成后沉淀经验
    - `$jetlinks-capture`
    - 如需回写项目规则，再加对应业务 skill
    - 如已抽象成通用 skill，再继续准备 `jetlinks-develop-skills` 官方 PR

## 输出要求

### 当用户要求先分析

输出：
1. 任务分类
2. 需要切换的 focused skill
3. 系统性求解触发、竞争假设与局部修补预算（如适用）
4. 代码检索问题、确认锚点、推断边和剩余不确定性（如适用）
5. 需要先确认的工作区事实
6. 建议落点和实现边界
7. 如果当前仓库参考实现很少，明确说明将切换到模板仓库模式

### 当用户要求直接实现

执行顺序：
1. 静默完成分类
2. 复杂或停滞任务先用 `$systematic-solving` 建立问题模型，并加载 JetLinks 扩展；同一假设下一次实现失败后停止编辑并重构。长任务同时用 `$task-continuity` 管理计划、恢复与阶段性交付
3. 没有精确 ownership / consumer / impact 锚点时，用 `$code-navigation` 按当前环境可用能力建立有界且带置信度的最小执行路径；需要时加载 JetLinks 领域扩展
4. 切换最少 domain-focused skill
5. 查看路径锚点和必要相邻代码
6. 实现最小完整闭环
7. 如果任务要求交付，再补原场景 / 同类代表 / 反例边界 / 回归证据、测试、提交与 PR 规范检查
8. 如果任务产出了跨任务稳定经验，再建议应更新的 canonical 来源或合理的新知识路径；单次完成总结不落档
9. 如果结论已成熟到可抽成通用 skill，再询问是否并入 `jetlinks-develop-skills` 并准备官方 PR
10. 只汇报最终规则结论、验证结果和风险，不输出操作流水
