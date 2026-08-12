# JetLinks 代码导航领域扩展

本文件只扩展 `$code-navigation` 在 JetLinks 工作区中的领域关系。通用检索顺序、证据强度、查询边界、新鲜度和降级规则仍由 [`../../code-navigation/SKILL.md`](../../code-navigation/SKILL.md) 负责。

## 1. 工作区事实

JetLinks 任务先按当前仓库实际情况识别：

- Maven / Gradle 或其他真实构建入口、父子聚合与模块声明。
- manager / core 等已有分层与 owning module。
- 软链接、外部子工程、多仓边界和项目内入口路径。
- Java / Kotlin、Vue / TypeScript 或其他实际存在的语言与生成代码。

这些是常见候选，不是固定前提。若当前工作区使用不同构建、语言或目录，以实际配置为准。

## 2. 领域节点与关系

在通用节点 / 边之上按需增加：

```text
Endpoint, Command, Event, Topic, AssetType,
ProtocolProvider, Codec, Parser, TraceSpan, MBean,
VueComponent, FrontendRoute, ApiClient, EnumDictionary
```

```text
EXPOSES_ENDPOINT, HANDLES_COMMAND,
PUBLISHES_EVENT, SUBSCRIBES_TOPIC,
CHECKS_ASSET_PERMISSION,
PROVIDES_PROTOCOL, ENCODES, DECODES,
EMITS_TRACE, MANAGES_RUNTIME,
USES_COMPONENT, CALLS_API, CONSUMES_ENUM
```

每个新增关系都必须保留方向、locator、source fingerprint、extractor / evidence 和 confidence，不能折叠为模糊的“依赖”。

## 3. 高频领域路径

按任务实际涉及范围选择，不默认全部抽取：

- Controller endpoint → application service → repository / query path。
- `CommandSupport.execute(...)` / command ID → provider / handler → 结果消费者。
- event publisher → listener；Topic publisher → `@Subscribe` 或动态 subscriber 候选。
- CRUD / 自定义接口 / command / subscription → `AssetsHolder` 查询注入、操作断言、资产过滤和 `AssetType`。
- `ProtocolSupportProvider` → transport codec / parser → 上下行消息关联。
- 关键业务阶段 → TraceHolder span；常驻组件 → MBean 管理入口。
- frontend route → page → component → API client → backend endpoint。
- `EnumDict` / `I18nEnumDict` → 前端 `{value,text}` 展示与提交消费者。

## 4. 证据约束

- Maven module ownership 必须由当前构建声明确认；import、目录邻近和图 community 只能提供候选。
- Java / TypeScript / Vue 的精确 symbol 关系优先使用当前环境可用的 compiler / language service；没有时降级到声明、导入、配置和源码复核。
- Command ID、Topic、协议 route、权限动作和前端 API 可能由常量、配置或运行时拼接产生。无法完整解析时标为 `INFERRED` / `AMBIGUOUS`。
- Spring 代理 / 装配、多个 provider、反射、动态订阅和 runtime registration 不得由类名相似度直接判定目标。
- 高影响领域边需要当前配置、测试、trace 或最小运行时证据复核；`RUNTIME` 证据同时记录产品、设备、租户、节点、输入和时间范围等适用边界。

## 5. 组合方式

- 模块落点：`$code-navigation` + `$jetlinks-routing`。
- 复杂 / 停滞问题：`$code-navigation` + `$systematic-solving` + 本文件 + owning domain skill；长任务再组合 `$task-continuity`。
- 变更影响与测试候选：`$code-navigation` + owning domain skill + `$jetlinks-delivery`。
- 已有 Recovery Capsule 精确锚点且 source fingerprint 匹配：只从锚点继续，不因为本扩展存在而重新扫描全部 JetLinks 领域关系。
