# JetLinks Web Capability Reuse Rules

本文件整合组件、hooks、utils 与包级能力地图。用于在实现前先判断可复用能力，减少重复开发。

## 先确认的工作区事实

- 组件导出入口优先核验 `jetlinks-web-core/src/components/index.ts`。
- hooks 导出入口优先核验 `jetlinks-web-core/src/hooks/index.ts`。
- utils 导出入口优先核验 `jetlinks-web-core/src/utils/index.ts`。
- 如果目录或导入方式与本文不同，以当前工作区真实结构为准。

## 包级能力复用优先级

1. 页面搭建优先：`@jetlinks-web-core/components`
2. 逻辑复用优先：`@jetlinks-web-core/hooks`，再看 `@jetlinks-web/hooks`
3. 通用函数优先：`@jetlinks-web-core/utils`，再看 `@jetlinks-web/utils`
4. 常量与底层能力按需使用：`@jetlinks-web/constants`、`@jetlinks-web/core`

## 页面组件组合

以下名称是候选能力，使用前必须核验导出与契约。

先完成页面分型，再让用户确认页面壳层或风格，再选组件组合。只有页面已明确判断为标准管理页时，才进入“搜索层 + 列表层 + 编辑层”的管理页组合判断；如果核心任务是监控、分析、处置、流程推进或详情理解，应先选更贴近业务的页面结构，再回头挑组件。对管理页中的通用条件搜索，如果 workspace 已提供 `ConditionFilter` 及其编码/回显工具，默认先用它承接搜索层。

| 场景 | 推荐组合 | 说明 |
| --- | --- | --- |
| 标准管理列表页（通用条件搜索） | `FullPage` + `ConditionFilter` + `j-pro-table` | 标准管理页默认优先组合 |
| 标准管理列表页（旧页兼容 / 轻量固定筛选） | `FullPage` + `ProSearch` + `j-pro-table` | 仅在相邻页面稳定沿用或筛选很轻时使用 |
| 卡片列表页 | `j-pro-table(card)` + `CardBox` + `BatchDropdown` | 卡片化资源管理 |
| 管理页内新增/编辑 | `EditDialog` | 仅用于管理页或明确的子流程编辑 |
| 行内编辑 | `InputEditable` / `Editable` / `FormItemEditable` | 减少重复弹窗 |
| 条件构建 | `TermsCascader` / `TermsCascaderGroup` | 复杂条件统一处理 |
| 上传导入 | `ProUpload` / `ImageUpload` / `BatchImport` | 上传与模板导入 |
| 地图与轨迹 | `AMapComponent` / `SelectAMap` / `PathSimplifier` | 地图能力封装 |
| 图表与时间 | `JEcharts` / `JDashboardTimeSelect` | 仪表盘与趋势分析 |
| 动态扩展位 | `RegistryComponent` / `RemoteComponent` | 运行时扩展 |

## 高频组件关键契约

- `ConditionFilter`：关注字段定义、条件模型、`encodeConditionFilterQuery` / `decodeConditionFilterQuery`、远程选项回显
- `ProSearch`：关注 `columns`、`target`、`@search`
- `j-pro-table`：关注 `columns`、`request`、`params`
- `EditDialog`：关注 `schema`、`request`、`@save`、`@close`
- `BatchImport`：关注 `downloadUrlBuilder`、`request`、`@save`
- `RegistryComponent`：关注 `code` 和插槽位置
- `RemoteComponent`：关注 `remoteName`、`componentName`、`componentProps`

## 组件引入策略

- 对页面内非首屏关键、按需展示或体积较大的本地组件，优先使用异步组件引入，减少首屏包体积。
- 不要默认使用 `import TestComponent from './xxxx/index.vue'` 这种同步引入方式；优先改为 `defineAsyncComponent`。
- 推荐写法：

```ts
import { defineAsyncComponent } from 'vue';

const TestComponent = defineAsyncComponent(() => import('./xxxx/index.vue'));
```

## Hook 选型

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

### 路由与菜单

- `handleMenus`：菜单树与动态路由装配
- `handleAuthMenu`：按钮权限映射
- `routerFallback`：页面回退处理

### 查询编码与条件处理

- `paramsEncodeQuery`：编码 `terms[]/sorts[]`
- `encodeConditionFilterQuery` / `decodeConditionFilterQuery`：统一条件筛选路由编码与回显
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

## 推荐工作流

1. 先做页面分型与风格确认，再做包级能力评估，最后进入具体组件/Hook/utils 选型。
2. 优先组合现有能力，避免页面内重复封装。
3. 管理页若存在通用搜索，先判断 `ConditionFilter` 是否应承担搜索层，再衔接列表、编辑、回传等主流程。
4. 无法复用时给出原因：能力缺口、兼容约束或性能约束。

## 约束

- 不要把文档中的能力清单当作固定事实，必须先核验导出与签名。
- 不要绕过 `handleMenus`/`handleAuthMenu` 在页面硬编码权限映射。
- 不要在多处手工拼接查询参数，优先复用编码工具。
- 不要用组件内零散 watcher + 回调替代已有 hook 组合能力。
- 不要因为组件现成就反向决定页面结构；业务分型优先于组件组合。
- 不要在页面壳层/风格还未让用户确认前，就直接进入传统 CRUD 组件组合。
- 不要在 workspace 已提供 `ConditionFilter` 工具链时，仍把 `ProSearch` 当成通用搜索默认值。
- 不要在未确认真实数据源、刷新方式和业务用途前引入统计卡、趋势图或 `JEcharts` 相关区块。

## 自检清单

- 是否优先复用已存在的包级能力。
- 是否复用了匹配场景的组件组合与 Hook 模式。
- 是否避免了同类 utils 在页面侧重复实现。
- 若未复用，是否提供了可验证的理由。
