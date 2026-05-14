# JetLinks Web Development Rules

本文件是 `jetlinks-web` 的核心入口文档。先读本文件，再按任务需要加载其他参考文档。

## 任务分类

- 页面实现或改造：列表页、详情页、弹窗页、配置页
- 仪表盘组件：`visDashboard` 运行组件、配置面板、设计器接线
- 能力复用：组件、hooks、utils、包级能力选择
- 目录落点：代码放 `jetlinks-web-core` 还是 `modules/*-ui`
- 样式规范：颜色、圆角、阴影、字号、工具类和局部 Less 约束
- 状态治理：本地状态、路由状态、store、服务端状态边界
- 质量与类型：交付质量、TypeScript 风险控制

## 标准工作流

1. 先查看目标模块相邻页面，确认真实技术栈、命名、交互风格。
2. 先核验工作区事实，再写代码：导出入口、依赖包、模块目录、已有示例。
3. 先做能力复用评估，再决定是否新增实现。
4. 只加载最小必要参考文档，不一次性读取全部 references。
5. 使用最小完整改动完成需求，优先沿用现有页面组合和模块边界。
6. 按质量与类型约束做交付前自检，补充可验证路径。

## 新页面 / 新模块落地 Checklist

落地新页面前按以下顺序检查：

1. 确认目录落点：先判断代码应放在 `jetlinks-web-core`、`@jetlinks-web` 公共能力，还是具体 `modules/*-ui` 业务模块。
2. 查看相邻页面：优先参考同模块已有页面的路由、布局、搜索、表格、弹窗、详情块、样式和 API 组织方式。
3. 确认页面壳与组合：标准管理页优先评估 `FullPage + ProSearch + j-pro-table`；新增/编辑优先评估 `EditDialog`。
4. 确认公共能力：先查 `@jetlinks-web-core/components`、hooks、utils 和 `@jetlinks-web` 相关能力，避免重复实现。
5. 确认跨模块边界：不要直接引用其他业务模块内部组件、hooks、utils 或私有类型；确需复用时先评估公共导出或能力上沉。
6. 确认数据与 API：API 请求统一放入 `api/*.ts` 或既有 store action，页面不硬编码接口、base、token 或上传 header。
7. 确认状态归属：临时 UI 状态放本地；跨页面/全局状态走 store；可分享筛选、Tab、回跳上下文走路由参数。
8. 确认权限与菜单：按钮权限、菜单、动态路由优先复用 `handleMenus`、`handleAuthMenu` 和既有权限体系。
9. 确认基础控件：按钮、输入、选择、日期、弹窗、表格、分页、空状态等优先使用 Ant Design Vue 或 JetLinks 项目组件，原生交互标签只用于有明确理由的场景。
10. 确认卡片语义：卡片、资源块、列表项容器优先使用 `CardBox`、`j-pro-table(card)`、`a-card`、相邻卡片组件或语义化 `div`/`section`，不要把整张卡片写成 `button`。
11. 确认样式体系：优先沿用相邻页面、Design System、Ant Design Vue 和已有变量，不临时创造新的视觉体系。
12. 确认质量边界：页面保持薄，复杂逻辑抽到 hook、store、utils 或子组件；补齐关键类型、loading、empty、error 和验证路径。

## 页面薄化硬规则

- 页面 SFC 只负责路由参数读取、数据接入、组件组合、事件分发和轻量状态编排。
- API 请求不得直接写在页面组件内，统一下沉到 `api/*.ts`、已有 store action 或已有请求封装。
- 复杂数据转换、联动逻辑、权限判断、跨组件副作用优先抽离到 hook、store、utils 或局部子组件。
- 页面内新增子区域超过一个完整业务块时，优先拆为局部子组件；页面负责传参和接收事件。
- 标准管理页优先沿用相邻页面的页面壳、搜索、表格、弹窗、详情块和样式组合。
- 拆分组件时保持职责清晰，不为了减少行数制造过深包装层。

## 组件复用前置 Checklist

新增页面、弹窗、详情块、卡片、筛选器、状态标签或操作区前，必须按以下顺序检查：

1. 先看目标模块相邻页面，确认真实使用的布局、组件、交互和样式模式。
2. 再查 `@jetlinks-web-core/components` 是否已有等价组件或组合能力。
3. 再查 `@jetlinks-web` 是否已有项目级组件、hooks、utils 或 constants 可复用。
4. 再查 Ant Design Vue 是否已有对应基础控件或交互组件。
5. 再查当前模块内是否已有局部公共组件、配置项、hooks 或枚举映射。
6. 如果已有能力能覆盖主要场景，优先通过 props、slots、配置项、组合或局部适配复用。
7. 只有在能力缺口、契约不兼容、性能约束或交互差异明确时，才新增组件、hook 或 utils。
8. 新增能力时必须保持模块边界，不得深层引用其他业务模块内部文件。
9. 无法复用现有能力时，在交付说明中简要说明原因。

## 基础控件与卡片语义规则

- Ant Design Vue 是基础交互控件的默认优先选择，不是绝对禁止原生标签；按钮、输入、选择、日期、弹窗、抽屉、提示、表格、分页、空状态等先评估 `a-*` 组件或项目封装。
- 标准业务列表、筛选、编辑、上传、卡片、条件构建优先评估 JetLinks 高阶组件，例如 `ProSearch`、`j-pro-table`、`EditDialog`、`ProUpload`、`CardBox`、`TermsCascader`。
- 原生 `div`、`section`、`span` 等可以用于语义化结构和布局，但不要用原生 `button`、`input`、`select`、`textarea`、`table` 替代已有交互组件。
- 卡片、资源块、列表项根节点是内容容器，不应使用原生 `button` 承载整块布局；优先使用 `CardBox`、`j-pro-table(card)`、`a-card`、相邻页面卡片组件或语义化 `div`/`section`。
- 如果整张卡片可点击，仍应使用卡片容器承载布局，并通过点击事件、hover/active 样式以及必要的 `role`、`tabindex`、键盘事件表达交互，而不是把卡片写成 `button`。
- 只有当元素本身就是单一动作按钮且不承载复杂内容时，才使用 `a-button` 或必要的原生 `button`；卡片内的新增、编辑、删除、查看等操作按钮优先使用 `a-button` 或项目操作组件。
- 使用原生交互标签时，需要有明确理由，例如组件库无法满足语义、第三方库插槽限制、可访问性特殊要求或性能约束，并补齐禁用态、loading、校验态、键盘交互和可访问性。

## 标准页面组合白名单

以下是标准业务页面的默认优先组合，使用前必须以当前工作区真实导出和相邻页面示例为准：

| 场景 | 默认优先组合 | 说明 |
| --- | --- | --- |
| 标准管理列表页 | `FullPage` + `ProSearch` + `j-pro-table` | 查询、分页、表格、操作列优先复用该组合 |
| 卡片资源列表页 | `j-pro-table(card)` + `CardBox` + `BatchDropdown` | 资源卡片、批量操作、卡片操作区优先复用 |
| 新增/编辑弹窗 | `EditDialog` | 配置驱动表单优先，不重复手写弹窗表单 |
| 详情页 / 详情块 | 相邻页面详情组件 + 局部 section 组件 | 优先复用模块内已有详情结构 |
| 行内编辑 | `InputEditable` / `Editable` / `FormItemEditable` | 简单字段编辑优先避免新增弹窗 |
| 条件构建 | `TermsCascader` / `TermsCascaderGroup` | 复杂查询条件、规则条件统一处理 |
| 上传导入 | `ProUpload` / `ImageUpload` / `BatchImport` | 上传请求头、模板下载、导入流程优先复用 |
| 图表趋势 | `JEcharts` / 相邻图表封装 | 不在页面内重复初始化 ECharts |
| 运行时扩展 | `RegistryComponent` / `RemoteComponent` | 动态扩展位、远程组件优先使用现有机制 |

- 白名单是优先级，不是盲用清单；实际使用前必须核验导出、props、事件和相邻示例。
- 不得因为白名单里有名称就发明不存在的 props、emits、hook 签名或 utils API。

## 按场景加载文档

- 能力复用与组件/Hook/utils 选型：[`capability-reuse-rules.md`](capability-reuse-rules.md)
- `visDashboard` 仪表盘组件开发：[`dashboard-component-rules.md`](dashboard-component-rules.md)
- 模块与文件落点：[`directory-structure-rules.md`](directory-structure-rules.md)
- 状态边界与 store 使用：[`state-management-rules.md`](state-management-rules.md)
- 样式变量与工具类约束：[`style-rules.md`](style-rules.md)
- 质量与类型约束：[`quality-and-type-rules.md`](quality-and-type-rules.md)
- 示例查找入口：[`example-locations.md`](example-locations.md)
- 快速导航总览：[`index.md`](index.md)

## 核心约束

- 不要发明不存在的组件契约、hook 签名或 utils API。
- 不要绕开已有 `@jetlinks-web-core`/`@jetlinks-web` 能力重造同类实现。
- 不要把文档中的能力名称当作固定事实，必须以当前工作区导出为准。
- 不要在页面内硬编码路由权限、菜单元数据、API base 或 token 行为。
- 不要在组件内硬编码设计值；颜色、圆角、阴影、字号优先复用 `comm.less` 变量或工具类。
- 不要把一次任务扩展成大范围结构重写，优先最小改动、可验证交付。

## 自检清单

- 是否已核验目标能力在当前工作区真实存在。
- 是否优先复用了现有组件、hooks、utils 或 store 契约。
- 是否保持了模块边界、目录风格和页面交互一致性。
- 是否完成了关键交互、状态流、路由权限和类型风险验证。
