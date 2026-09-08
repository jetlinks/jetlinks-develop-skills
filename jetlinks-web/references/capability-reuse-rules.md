# JetLinks Web Capability Reuse Rules

本文件用于新增能力、选择组件或改变抽象边界时判断复用。仅修改已知组件的文案、样式、字段或 props 时，沿相关契约和相邻代码处理，不触发全部搜索层级。

## 先确认的工作区事实

- 涉及 core 能力时，先读 [`core-capability-docs.md`](core-capability-docs.md)，再按任务读取 `jetlinks-web-core/src/README.md` 和对应分类 README；这些文档只做导航，最终仍以导出、源码和生产代码为准。
- `@jetlinks-web/components` 共享基础组件：先读 `packages/components/src/components.md` 做场景导航，再用 `packages/components/src/components.ts` 核验根导出，最后只打开候选组件文档与源码。
- `@jetlinks-web-core/components` 项目级组件：先读 `jetlinks-web-core/src/components/README.md` 定位候选，再核验 `jetlinks-web-core/src/components/index.ts`、组件源码和相邻生产用法。
- hooks：先读 `jetlinks-web-core/src/hooks/README.md`（若存在），再核验 `jetlinks-web-core/src/hooks/index.ts`。
- utils：先读 `jetlinks-web-core/src/utils/README.md`（若存在），再核验 `jetlinks-web-core/src/utils/index.ts`。
- store：先读 `jetlinks-web-core/src/store/README.md`（若存在），再核验 `jetlinks-web-core/src/store/index.ts` 和对应 Store 源码。
- 如果目录、包版本或导入方式与本文不同，以目标项目当前依赖、真实导出和生产代码为准。
- `jetlinks-project-ui-cli` 只能在用户明确要求时作为外部参考；不能作为当前 workspace 可用组件的证据。

## 包级能力复用优先级

1. 共享基础组件：先从 `@jetlinks-web/components` 映射文档判断是否已有输入、展示、搜索、表格、图标、布局或权限控件。
2. 项目级业务组件与稳定封装：再看 `@jetlinks-web-core/components`；若它已封装基础组件并承载权限、i18n、路由、注册或业务组合约定，优先使用该封装。
3. 基础交互控件：两层都没有合适能力时评估 Ant Design Vue，再考虑原生标签。
4. 逻辑复用：优先 `@jetlinks-web-core/hooks`，再看 `@jetlinks-web/hooks`。
5. 通用函数：优先 `@jetlinks-web-core/utils`，再看 `@jetlinks-web/utils`。
6. 常量与底层能力：按需使用 `@jetlinks-web/constants`、`@jetlinks-web/core`。

## Ant Design Vue 与原生标签边界

- 基础交互控件优先使用 Ant Design Vue：`a-button`、`a-input`、`a-input-number`、`a-select`、`a-radio`、`a-checkbox`、`a-switch`、`a-date-picker`、`a-time-picker`、`a-upload`。
- 反馈与容器类交互优先使用 Ant Design Vue：`a-modal`、`a-drawer`、`a-popconfirm`、`a-tooltip`、`a-alert`、`a-empty`、`a-spin`、`a-pagination`。
- 数据展示优先评估项目级 `j-pro-table`；确需基础表格时使用 `a-table`，不要手写 `<table>`、分页、loading 和 empty 状态。
- 表单优先使用 `a-form` / `a-form-item` 或项目级 `EditDialog` schema，不在页面里堆叠原生 `<label>`、`<input>` 与手写校验。
- 原生标签不是禁用项；`div`、`section`、`span` 等可用于结构和布局，但不应用原生交互控件绕过组件库能力。

## 卡片列表根节点规则

- 卡片列表优先复用 `j-pro-table(card)`、`CardBox` 或相邻页面已有卡片布局模式。
- 卡片、资源块、列表项容器不要使用原生 `button` 作为根节点；卡片根节点优先使用 `CardBox`、`a-card`、模块内卡片组件或语义化 `div`/`section`。
- 整卡点击场景应在卡片容器上声明点击行为与状态样式；必要时补充 `role="button"`、`tabindex="0"` 和键盘事件，不要为了点击能力把整张卡片写成 `button`。
- 卡片内部的具体操作按钮使用 `a-button` 或项目操作组件，避免原生 `button` 造成主题、尺寸、权限、loading、禁用态和 hover/focus 风格不一致。
- 只有单一动作、无复杂内容承载的元素才适合按钮语义；复杂卡片内容、状态、描述和操作区混合时必须保持卡片容器语义。

## 复用搜索优先级

新增 component / hook / service / API wrapper / util 前，从当前锚点向相关层逐级搜索；找到适合且已验证的能力即停止，已有效的结果可以复用。以下是候选范围，不要求扫描所有范围或逐项提交证明：

1. 当前功能目录：目标页面附近的 `components/**`、`hooks/**`、`utils/**`、`api/**`、`services/**`、`types/**`、schema/config。
2. 当前模块：`modules/<module>-ui/**` 下相似页面、组件、hook、工具函数、store、API/service。
3. 同业务域或兄弟子模块：对象模型、流程、字典、权限、搜索、表格操作、表单弹窗、数据转换相同或高度相似的 `modules/*-ui/**` 实现。
4. 共享层：先查 `@jetlinks-web/components`（`packages/components/src/components.md` → `components.ts` → 单组件文档/源码），再查 `@jetlinks-web-core/components`（`jetlinks-web-core/src/components/index.ts` → 组件源码），随后按需查其他 `@jetlinks-web-core/*`、`@jetlinks-web/*` 导出。
5. 跨模块公开出口：模块 `index.ts`、`register.ts`、注册中心、运行时扩展位、文档化 API。

原则：

- 同模块可直接复用符合本模块约定的内部能力。
- 跨模块复用必须优先走公开导出、注册中心或稳定扩展点。
- 对其他业务模块的私有实现，可以参考模式，但不要直接深层 import。
- 若多个实现相似，优先选择同模块或同业务域中最近维护、仍在使用的实现。
- 若现有能力只差少量适配，优先用 adapter/config/schema/slot 包装，不新建平行体系。

## 页面组件组合

以下名称是候选能力，使用前必须核验导出与契约。表中的 `ProTable`、`Search`、`CardSelect`、`AIcon`、`BadgeStatus`、`TimeFormat`、`ValueItem` 等共享基础组件，先从 `packages/components/src/components.md` 定位其独立文档并核验 `components.ts` 根导出；`ConditionFilter`、`QuickFilterSidebar`、`EntityCard`、`SectionCard`、`JlDrawerShell` 等项目级组件，则核验 `jetlinks-web-core/src/components/index.ts` 和相邻生产用法。

需要新增页面或改变主交互时先完成业务分型；已有明确授权与合理方案直接实施，只有实质未决选择才询问，再选相关组件组合。只有页面已明确判断为标准管理页时，才进入“搜索层 + 列表层 + 编辑层”的管理页组合判断；如果核心任务是监控、分析、处置、流程推进、对象详情理解或资源选择，应先选更贴近业务的交互方案，再回头挑组件。对管理页中的通用条件搜索，如果 workspace 已提供 `ConditionFilter` 及其编码/回显工具，默认先用它承接搜索层。

| 场景 | 推荐组合 | 说明 |
| --- | --- | --- |
| 标准管理列表页（通用条件搜索） | `FullPage` + `ConditionFilter` + `j-pro-table` | 标准管理页默认优先组合 |
| 标准管理列表页（旧页兼容 / 轻量固定筛选） | `FullPage` + `ProSearch` + `j-pro-table` | 仅窄改旧页、用户明确要旧表格风格，或筛选很轻且无路由回显 / 远程选项 / 保存搜索时使用；必须说明例外理由 |
| 资产卡片台账页 | `ConditionFilter` + `QuickFilterSidebar` + `ResponsiveGrid` + `EntityCard` / `CardBox` | 设备资产、资源、模型、应用、通道等对象 |
| 筛选工作台页 | `ConditionFilter` + `QuickFilterSidebar` + 摘要列表 / 卡片 | 高频筛选、状态处置、复杂记录定位 |
| 对象详情工作区 | 对象摘要 + `SectionCard` + `KvGrid` + `TabsCard` + `StickyActionBar` | 单对象理解、维护、局部编辑和关联记录 |
| 主从详情工作区 | 左侧树/列表 + 右侧 `SectionCard` / `TabsCard` | 列表浏览与单对象深度编辑并行 |
| 配置向导 / 能力开通页 | Steps / 分区表单 + `CardSelect` + `StickyActionBar` | 强流程配置、能力启用、通道开通 |
| 资源 / 能力选择器 | `MarketplaceResourcePicker` + `CardSelect` | 模型、模板、能力、插件、市场资源选择 |
| 完整新增/编辑 | `EditDialog` / `JlDrawerShell` / 独立配置页 | 仅用于字段多、依赖强或需要完整校验的流程 |
| 轻量单项编辑 | `InputEditable` / `Editable` / `FormItemEditable` | 名称、标签、说明、备注、描述等轻量字段 |
| 条件构建 | `ConditionFilter` / `TermsCascader` / `TermsCascaderGroup` | 优先字段驱动的通用条件、时间/范围、嵌套映射与选项值编辑 |
| 标签与状态 | `MetaChip` / `ChipGroup` / `AppTag` / `j-badge-status` | 状态、分类、能力标签和计数筛选 |
| 图标 | `AIcon` / `IconLibrary` / 当前项目图标资产 | 表达状态、动作或对象类型，不做无意义装饰 |
| 上传导入 | `ProUpload` / `ImageUpload` / `BatchImport` | 上传与模板导入 |
| 地图与轨迹 | `AMapComponent` / `SelectAMap` / `PathSimplifier` | 地图能力封装 |
| 图表与时间 | `JEcharts` / `JDashboardTimeSelect` | 仪表盘与趋势分析 |
| 动态扩展位 | `RegistryComponent` / `RemoteComponent` | 运行时扩展 |

## 高频组件关键契约

- `ConditionFilter`：关注字段定义、条件模型、`encodeConditionFilterQuery` / `decodeConditionFilterQuery`、远程选项回显
- `ProSearch`：关注 `columns`、`target`、`@search`，并先确认它只是旧页兼容或轻量固定筛选例外
- `j-pro-table`：关注 `columns`、`request`、`params`
- `EditDialog`：关注 `schema`、`request`、`@save`、`@close`
- `EntityCard` / `CardBox`：关注对象摘要、状态、标签、主动作和卡片选中态
- `SectionCard` / `KvGrid` / `TabsCard`：关注详情分区、键值字段和信息密度
- `InputEditable` / `Editable` / `FormItemEditable`：关注单字段保存、取消、校验和回显
- `JlDrawerShell` / `StickyActionBar`：关注抽屉结构、固定操作区和表单提交节奏
- `MetaChip` / `ChipGroup` / `AppTag`：关注状态、分类、数量和筛选联动
- `MarketplaceResourcePicker` / `CardSelect`：关注资源预览、筛选、选择和确认
- `BatchImport`：关注 `downloadUrlBuilder`、`request`、`@save`
- `RegistryComponent`：关注 `code` 和插槽位置
- `RemoteComponent`：关注 `remoteName`、`componentName`、`componentProps`

## 组件引入策略

- 对页面内非首屏关键、按需展示或体积较大的本地组件，优先使用异步组件引入，减少首屏包体积。
- 不要默认使用 `import TestComponent from './xxxx/index.vue'` 这种同步引入方式；优先改为 `defineAsyncComponent`。
- 推荐写法：

```ts
import { defineAsyncComponent } from 'vue';

// 非首屏关键组件异步加载：减小首屏包体积，组件首次渲染时才拉取 chunk
const TestComponent = defineAsyncComponent(() => import('./xxxx/index.vue'));
```

## Hook 选型

使用下列 Hook 前，先从 `jetlinks-web-core/src/hooks/README.md` 定位候选，再核验 `src/hooks/index.ts` 和相邻生产用法。

| Hook | 用途 | 关键点 |
| --- | --- | --- |
| `useTabSaveSuccess` | 打开新页，保存后回传当前页 | `onOpen` 传上下文参数 |
| `useTabSaveSuccessBack` | 保存后回传并返回 | `onBack` 可配 `onBefore` |
| `usePlatformContext` | 页面根级提供平台上下文 | 平台值以工作区实际实现为准 |
| `usePlatform` | 子组件读取平台上下文 | 用于平台差异渲染 |
| `isIotPlatform` | 快速平台判断 | 用于简单分支 |
| `useRegistryOptions` | 合并基础配置与注册项 | `autoSync` / `syncOptions` |
| `useRegistryVNodeMerge` | 合并默认节点与扩展节点 | `replace/before/after/append` |

## Utils 选型

使用下列工具前，先从 `jetlinks-web-core/src/utils/README.md` 定位候选，再核验 `src/utils/index.ts`、源码和副作用边界。

### 路由与菜单

- `handleMenus`：菜单树与动态路由装配
- `handleAuthMenu`：按钮权限映射
- `routerFallback`：页面回退处理

### 查询编码与条件处理

- `paramsEncodeQuery`：编码 `terms[]/sorts[]`
- `encodeConditionFilterQuery` / `decodeConditionFilterQuery`：统一条件筛选路由编码与回显（由 `ConditionFilter` 组件工具导出，见 `components/ConditionFilter/utils.ts`，不在公共 utils 中）
- `encodeQuery`：兼容旧查询结构
- `handleParamsToString`：固定分组条件字符串化
- `modifySearchColumnValue`：查询列值处理

### 通用能力

- `onlyMessage`：同类提示去重
- `getUploadHeaders`：上传请求头
- `getBaseApi`：统一 API base
- `getImageUrl` / `downloadJson`：资源展示与下载
- `transformTree` / `mergeObjectArrays`：树与集合处理
- `createScript`：动态加载外部脚本

## Store 选型

- 使用 Store 前先读取 `jetlinks-web-core/src/store/README.md`（若存在），判断状态是否跨页面共享，再核验 `src/store/index.ts` 和目标 Store 源码。
- 只有 `index.ts` 明确导出的 Store 才能作为根入口事实；未导出的 Store、菜单辅助文件和覆盖工具必须沿用已有深层生产导入，不因文件存在而扩大公共 API。
- 页面消费 Store 时优先使用 `storeToRefs` 读取响应式 state，动作直接调用 Store；请求、缓存、Scope 和持久化边界以 Store 与对应 utils 的真实实现为准。

## 推荐工作流

1. 先做业务分型与交互方案确认，再做包级能力评估，最后进入具体组件/Hook/utils 选型。
2. 优先组合现有能力，避免页面内重复封装。
3. 按卡片、列表、筛选、详情、轻量编辑、完整编辑、抽屉、底部操作、标签状态、图标、资源选择等场景映射组件。
4. 管理页若存在通用搜索，先判断 `ConditionFilter` 是否应承担搜索层；再按字段分型判断日期/时间、范围、布尔、选项、嵌套路径、无值条件等是否都能通过通用字段定义、标准条件和值编辑器表达，再衔接列表、编辑、回传等主流程。
5. 无法复用时给出原因：能力缺口、兼容约束或性能约束，并说明已核验的导出入口和相邻示例。

## 组件抽取决策流

函数封装、设计模式与组件边界的完整规则见 [`code-organization-rules.md`](code-organization-rules.md)。这里仅保留能力复用时的最短决策流。

出现重复结构时按以下路径判断：

1. 是否被 2+ 处消费？
   - 否 → 留在原处，不抽
   - 是 → 继续判断
2. 2+ 处的差异是"参数化可解"还是"语义根本不同"？
   - 参数化可解 → 评估抽组件，通过最小 prop / slot / 配置契约控制差异
   - 语义不同 → 各留各的，注释说明"视觉相似但语义不同"
3. 抽到哪里？
   - 同模块内 2+ 页面复用 → modules/<module>-ui/components/
   - 跨模块 2+ 模块复用 → jetlinks-web-core/components/
   - 仅 1 个模块用 → 先留模块内

### 不合并的反例

- ProSearch 和模块自定义筛选区：视觉相似但交互语义不同，不合并
- j-pro-table 的不同 columns 配置：同组件不同配置，不需要再封装一层
- 各模块的 register.ts：结构相似但注册内容不同，不合并
- 不同模块的详情页：布局相似但字段和业务逻辑不同，不应强行抽出"通用详情页"

## 重复结构抽取规则

- 第 1 次出现的业务结构，优先留在当前页面或当前局部组件内。
- 第 2 次出现相似结构时，先确认业务语义一致且差异可以通过 props、slots 或配置表达，再决定是否提炼为局部组件、配置项、hook 或小型 utils。
- 第 3 次出现相似结构时，必须评估是否沉淀为模块级公共组件、模块 hook、模块 constants，或上沉到公共能力；评估不等于强制合并。
- 抽取前必须判断差异是否能通过 props、slots、配置项或组合方式解决。
- 差异只是展示字段、标题、操作按钮、状态映射时，优先配置化，不复制整块模板。
- 差异涉及业务语义、接口上下文、权限体系或生命周期明显不同的，不要强行合并成复杂大组件。
- 新增通用组件时不以 props 数量作为硬门槛；如果 props / emits 代表多个不相关概念或泄漏父组件编排细节，应重新拆分职责或保留局部实现。
- 不为了减少文件行数制造过深包装层，组件层级应保持可读和可调试。

## 网格 / 列表布局约束

- 标准表格列表优先使用 `j-pro-table`，不要手写分页、loading、选择列和操作列的完整表格流程。
- 卡片列表优先评估 `j-pro-table(card)`、`CardBox` 或相邻页面已有卡片布局模式。
- 不要在多个页面重复手写相同的 `grid-template-columns`、卡片间距、响应式断点和批量操作区。
- 同类卡片网格第 2 次出现时，优先抽局部列表组件、配置项或统一样式类；第 3 次出现时评估模块级沉淀。
- 列表页必须明确 loading、empty、error、分页、筛选重置和刷新路径。
- 表格列、卡片字段、状态映射和操作按钮优先配置化，避免模板内重复堆叠条件判断。
- 大屏、窄屏或容器宽度变化明显的页面，应优先参考相邻页面响应式处理，不临时创造不一致断点。

## 约束

- 不要把文档中的能力清单当作固定事实，必须先核验导出、签名和目标项目实际安装版本。
- 不要把 `packages/components/src` 下存在的目录或文档直接当成 `@jetlinks-web/components` 根导出；根导出以 `components.ts` 为准。
- 不要根据源码目录自行拼接 `@jetlinks-web/components/es/...` 深层导入；只有目标版本和相邻生产代码均证明稳定可用时才沿用。
- 不要把外部组件库当成当前项目依赖；最终以当前 workspace 的 `@jetlinks-web/components` 与 `@jetlinks-web-core/components` 两层真实导出为准。
- 不要绕过 `handleMenus`/`handleAuthMenu` 在页面硬编码权限映射。
- 不要在多处手工拼接查询参数，优先复用编码工具。
- 不要用组件内零散 watcher + 回调替代已有 hook 组合能力。
- 不要因为组件现成就反向决定页面结构；业务分型优先于组件组合。
- 不要在交互方案还未让用户确认前，就直接进入传统 CRUD 组件组合。
- 不要在 workspace 已提供 `ConditionFilter` 工具链时，仍把 `ProSearch` 当成通用搜索默认值。
- 不要把“相邻页面仍使用 ProSearch”当成新页面的默认依据；除非是窄改旧页、用户明确要求旧表格风格，或当前筛选确实没有路由回显、远程枚举/引用选项和保存搜索需求，否则优先 `ConditionFilter`。
- 不要因为某个字段是“项目/用户/区域/字典”就直接新增字段专属搜索组件；先复用 `ConditionFilter` 的通用选项值编辑路径。
- 不要因为某个字段是时间范围、数值区间、嵌套路径或空值判断，就直接新增页面私有筛选组件；先复用标准条件、字段映射和通用值编辑器。
- 不要重复手写卡片、详情字段栅格、抽屉壳、底部操作条、标签筛选或轻量编辑组件。
- 不要为了编辑一个名称、标签、说明或备注而默认打开完整编辑表单。
- 不要在未确认真实数据源、刷新方式和业务用途前引入统计卡、趋势图或 `JEcharts` 相关区块。

## 自检清单

- 是否优先复用已存在的包级能力。
- 是否先通过 `packages/components/src/components.md` 按需定位共享基础组件，并用 `components.ts` 核验根导出。
- 是否复用了匹配场景的组件组合与 Hook 模式。
- 是否按交互方案映射了 `@jetlinks-web/components` 共享基础组件和 `@jetlinks-web-core/components` 项目级组件。
- 轻量字段是否优先使用单项编辑。
- 是否避免了同类 utils 在页面侧重复实现。
- 若未复用，是否提供了可验证的理由。
