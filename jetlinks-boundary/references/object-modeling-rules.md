# 属性、对象关系与语义声明的实现选择

负责人、所属组织、设备依赖、业务关联等需求在建模时读取。先判断事实及其 owner，再选择存储与声明方式；不以页面字段形状决定后端模型。

## 依赖方向

业务通过 `relation-component` 的公开对象 / 关系契约及 `jetlinks-core` 的通用模型、命令和语义注解声明能力。来源业务及其公共契约、core、relation 均不依赖任何 `ontology-*` 模块，不实现或导出 ontology 的 SPI / DTO，也不以其 HTTP 入口替代业务 / relation 契约。

ontology 在上层发现和消费 relation 的对象、关系、属性与动作，负责本体特有组合、路径、事实和证据。其内部适配由 ontology owner 和宿主装配，不能成为业务运行的前提；`ontology-core` 名称中的 core 不改变此边界。

## 从业务含义给出推荐

| 真实需要 | 推荐路径 |
| --- | --- |
| 设备增加保养周期、安装说明等依附值，没有独立对象身份 | 按 [版本化字段扩展](application-platform-rules.md#标准实体字段扩展) 保存属性，不为语义声明建立无意义对象 |
| 设备关联已有用户作为负责人，只需当前关联、增删和双向查找 | 先查现有事实 owner；无已有业务事实时优先复用 relation 托管关系，不默认新增 `ownerId` 扩展或应用中间表 |
| 负责人、空间归属或组织成员已由原业务权威维护 | 通过 relation 的原 Provider 暴露关系，修改仍走原业务动作；既有外键可继续承载事实，不向通用关系表双写 |
| 任职有审批、有效期、交接记录或独立权限 / 生命周期 | 业务 owner 承载任职 / 指派事实及必要约束，以 relation 暴露关系或独立对象，供各上层消费者使用 |
| 只给已有对象补充摘要属性、查询或动作 | 复用 `ObjectSupportProvider` / `AbstractObjectSupport`，不注册第二个身份 Provider，不建立 ontology 专属对象副本 |
| 管理员运行时新增“设备依赖控制器”等关系 | 使用 relation 的动态关系定义与授权维护入口，复用已有两端类型；不为每种配置生成实体或代码分支 |
| 目标制品没有所需的新注解 / 对象能力 | 核验旧版已有 relation 能力，必要时沿公开 SPI 适配；仍不足才补 owner 契约或应用表，不因未装 ontology 就放弃 relation |

只要求“当前唯一主负责人”时，核实关系 owner 的基数 / 原子替换能力；缺少时在正确 owner 补通用约束或复用业务写入口，不因一个唯一性要求新建审批、任职框架。

## 代码声明与动态配置

稳定产品语义随代码审查和版本交付；运行时由管理员增减关系种类时用动态配置。定义类型与维护具体关联是两种操作，代码声明不等于在初始化代码中写入具体负责人。

业务声明按实际职责选择原扩展点：

| 声明内容 | 公开入口及边界 |
| --- | --- |
| 新业务对象身份、类型和原业务关系 | `RelationObjectProvider`，通过 `getType()` 的 `ObjectType / Relation` 声明分类与关系，查询和关系取数仍由来源实现 |
| 权威实体生命周期事实 | `@ObjectEntity` 标记原身份实体；不是 Provider 自动生成器，也不适用于辅助记录 / 绑定表，不替代资产声明 |
| 已有对象的补充属性或动作 | Spring Bean 上 `@ObjectSupport` 配合 `AbstractObjectSupport`；原方法使用 `@CommandHandler`，无参数且至多返回一个值的查询可加 `@PropertySource` |
| 字段、模型及功能语义 | core 的 `@SemanticRole / @SemanticTypes / @FunctionSemantics` 或原元数据扩展；功能明确区分 query / action，声明不替代实际授权与执行 |
| 既有 ID 字段指向其他对象 | `@PropertyReference` 描述目标类型、原关系及可选名称字段；不自动创建关系、存储或查询，展示名称不证明目标存在或可编辑 |

关系仍沿现有 relation SPI 声明与实现，不能把 `@ObjectSupport` 当任意关系注册注解。已有对象缺少必要扩展点时，在 relation owner 补通用契约并交付，不转向 ontology SPI 绕过边界，也不注册第二个同类型 Provider。

对象属性、只读查询或事件用作指标来源，以及业务对象关联指标 / 按归属汇总时，按 [统一指标复用](platform-capability-reuse-rules.md#自定义业务来源与多级汇总) 选择接入；语义声明不能代替历史证据、授权或新建一套业务计算引擎。

定义来源与事实 owner 分别核实：业务关系走原 Provider / 动作，托管关联走 relation 存储和正式授权入口；反向导航表示同一事实。固定声明、动态定义的冲突及读写路由以目标版本为准，仅设置 `instanceSource=managed` 不能证明全部导航、查询和写入入口都支持该组合。

## 能力与验证边界

- 2.21 及以后的新增语义 / 注解能力仍需核验 BOM、制品及 relation / core 装配；开发分支的 `@since` 不证明已发布。字段扩展、关系存储、语义元数据和 ontology 是不同能力，不捆绑启用。
- 关系声明和句柄不证明对象存在或已获权限；实际来源保留授权和状态校验，托管维护检查两端可见与规范源端写权限。按 [AssetsHolder](../../jetlinks-assets-permission/SKILL.md) 处理数据权限；`@ObjectEntity` 不替代 `@Asset` 与 `ExtendableEntity` 契约，组织成员或设备可见也不自动等于负责人。
- 托管边去重不保证唯一负责人，也不自动提供任意关系属性或有效期历史。单选 UI 和写前查重不能替代并发不变量，当前关联不能回答历史任职。
- 查询、分页、count 和导出按实际入口验证。relation 的 `PagerResult` 与 ontology 的候选 `items / hasMore` 不是同一契约；不把后者推广为通用关系分页，也不能先取一页设备再按负责人过滤。
- 验证业务声明与操作在其所需 relation 装配下可独立于 ontology 使用；本体接入验证由消费方承担。跨服务沿 [命令契约](cross-service-call-rules.md)，缺能力在正确 owner 补齐，不复制注册中心、解析器或平行授权。

源码先查 relation 的 `RelationObjectProvider`、`ObjectSupportProvider / AbstractObjectSupport`、`RelationObjectManager`、`ManagedRelationOperations / Reader` 及注解包；通用语义查 core 的 `MetadataSemantics` 和注解。仅审查本体消费时，再沿其 relation 适配器读取，不能把消费端 API 当成来源业务扩展点。

## 如何向用户解释

先根据需求和已有事实给推荐，例如：“设备和用户已是平台对象，建议复用关系能力；固定负责人语义由代码声明，管理员需要自行增加关系种类时用动态配置，业务无需依赖本体模块。”只有仍会改变模型的业务事实才追问，如唯一主责、有效期或审批；上下文已明确时直接推进。

界面沿原对象选择器、关联展示与原位维护表达业务语义。业务用户选择具体负责人，声明方式和事实来源由实现解释，不做成普通用户的必填技术选项。

## 建模依据

- W3C [Defining N-ary Relations](https://www.w3.org/TR/swbp-n-aryRelations/)（2006，Working Group Note）：当关系自身需要附加属性或涉及多个角色时，可将其建模为关系实例。用于判断任职 / 指派是否值得独立表达，不要求引入 RDF、OWL 或图数据库。
- W3C [Organization Ontology](https://www.w3.org/TR/vocab-org/)（2014，Recommendation）的 `Membership / Role / memberDuring`：区分人员、组织、角色与有时间范围的任职。可借鉴语义划分，不能据此宣称平台已有任职、有效期或标准推理能力。
