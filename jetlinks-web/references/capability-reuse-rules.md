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

| 场景 | 推荐组合 | 说明 |
| --- | --- | --- |
| 标准管理列表页 | `FullPage` + `ProSearch` + `j-pro-table` | 默认优先组合 |
| 卡片列表页 | `j-pro-table(card)` + `CardBox` + `BatchDropdown` | 卡片化资源管理 |
| 新增/编辑弹窗 | `EditDialog` | 配置驱动表单优先 |
| 行内编辑 | `InputEditable` / `Editable` / `FormItemEditable` | 减少重复弹窗 |
| 条件构建 | `TermsCascader` / `TermsCascaderGroup` | 复杂条件统一处理 |
| 上传导入 | `ProUpload` / `ImageUpload` / `BatchImport` | 上传与模板导入 |
| 地图与轨迹 | `AMapComponent` / `SelectAMap` / `PathSimplifier` | 地图能力封装 |
| 图表与时间 | `JEcharts` / `JDashboardTimeSelect` | 仪表盘与趋势分析 |
| 动态扩展位 | `RegistryComponent` / `RemoteComponent` | 运行时扩展 |

## 高频组件关键契约

- `ProSearch`：关注 `columns`、`target`、`@search`
- `j-pro-table`：关注 `columns`、`request`、`params`
- `EditDialog`：关注 `schema`、`request`、`@save`、`@close`
- `BatchImport`：关注 `downloadUrlBuilder`、`request`、`@save`
- `RegistryComponent`：关注 `code` 和插槽位置
- `RemoteComponent`：关注 `remoteName`、`componentName`、`componentProps`

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

1. 先做包级能力评估，再进入具体组件/Hook/utils 选型。
2. 优先组合现有能力，避免页面内重复封装。
3. 先打通查询、列表、编辑、回传等主流程，再补细节交互。
4. 无法复用时给出原因：能力缺口、兼容约束或性能约束。

## 约束

- 不要把文档中的能力清单当作固定事实，必须先核验导出与签名。
- 不要绕过 `handleMenus`/`handleAuthMenu` 在页面硬编码权限映射。
- 不要在多处手工拼接查询参数，优先复用编码工具。
- 不要用组件内零散 watcher + 回调替代已有 hook 组合能力。

## 自检清单

- 是否优先复用已存在的包级能力。
- 是否复用了匹配场景的组件组合与 Hook 模式。
- 是否避免了同类 utils 在页面侧重复实现。
- 若未复用，是否提供了可验证的理由。
