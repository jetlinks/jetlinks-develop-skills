# JetLinks Web Component Source Rules

本文件用于确认前端组件、hooks、utils 和交互样例的来源优先级，避免混淆共享基础组件、项目级业务组件、业务局部组件和外部参考。

## 两层组件事实源

### 1. `@jetlinks-web/components`：共享基础组件层

1. 先定位当前 workspace 的 `packages/components/src/components.md`。
   - 它是 AI 的轻量导航入口：按业务场景找到候选组件，再只打开候选目录中的 `组件名.md`。
   - 不一次性加载全部组件文档，不把文档目录名直接当作根导出名。
2. 再核验 `packages/components/src/components.ts`。
   - 只有这里的导出才能证明组件可从 `@jetlinks-web/components` 根入口具名导入。
   - 目录存在、组件有文档或自身有 `install`，都不能证明根入口或整包插件可达。
3. 需要确认 Props、emits、slots、默认值或内部边界时，再读对应组件源码。
4. 核验目标项目实际安装的 `@jetlinks-web/components` 版本和相邻生产导入；源码工作区与目标依赖版本不一致时，以目标项目实际可用契约为准。
5. 深层 `@jetlinks-web/components/es/...` 导入必须同时有目标版本构建产物和相邻生产代码证据，不根据源码目录自行拼接路径。

### 2. `@jetlinks-web-core/components`：项目级组件层

1. 若存在，先读取 `jetlinks-web-core/src/README.md` 和 `jetlinks-web-core/src/components/README.md`，按场景定位 1～3 个候选组件；不要一次性打开全部组件 README。
2. 再核验当前 workspace 的 `jetlinks-web-core/src/components/index.ts`。
   - 这是项目级业务组件、业务壳、共享组合和适配组件的导出事实源。
3. 再读候选 `jetlinks-web-core/src/components/*`。
   - 用于核验 Props、emits、slots、权限、i18n、路由、注册机制和真实能力边界。
4. 查看当前业务模块或相邻模块的真实用法。
   - 用于确认本项目如何组合基础组件与项目级组件，以及如何处理状态和交互反馈。

### 3. Core 其他能力层

- hooks：先读 `jetlinks-web-core/src/hooks/README.md`（若存在），再核验 `src/hooks/index.ts`、候选 Hook 源码和相邻生产用法。
- utils：先读 `jetlinks-web-core/src/utils/README.md`（若存在），再核验 `src/utils/index.ts`、候选工具源码和调用方；区分纯函数与请求、路由、存储等副作用。
- store：先读 `jetlinks-web-core/src/store/README.md`（若存在），再核验 `src/store/index.ts`、目标 Store 源码和相邻页面；区分根入口导出与深层路径。
- core 页面：先读 `jetlinks-web-core/src/views/README.md`（若存在），再核验真实路由入口、API、权限、Store/Hook 和页面源码。

### 4. 两层选择原则

- `@jetlinks-web/components` 适合跨项目共享的输入、展示、表格、搜索、图标、布局、权限按钮等基础能力。
- `@jetlinks-web-core/components` 适合 JetLinks 项目级业务组件、共享业务壳，以及带权限、i18n、路由、注册和跨组件组合约定的封装。
- 两层都能满足需求时，优先使用当前项目已稳定使用的 `@jetlinks-web-core` 封装，不绕过项目级契约。
- 项目级没有对应封装时，直接复用 `@jetlinks-web/components`；不要为换名称或转发 Props 再造一层无职责包装。

### 4. 用户明确指定的外部参考

- `jetlinks-project-ui-cli` 只在用户明确要求参考时查看。
- 它不能作为默认依赖、默认导入来源或当前项目组件存在性的证据。

## 新版样例提取规则

- 可参考设备资产管理、视频资源、巡检、通知配置、AI 模型/应用等页面的交互方案。
- 只借鉴业务相似的页面结构、筛选方式、详情承载、编辑节奏和状态反馈。
- 不复制业务字段、指标、接口路径、权限码、局部组件实现或样例数据。
- 不把另一个业务页面的功能介绍、统计卡、流程步骤直接搬到当前业务。
- 外部优秀设计只补充交互思路，不覆盖 JetLinks 当前组件体系和 Ant Design / Ant Design Vue 基线。

## 硬约束

- 不要在技能默认流程中要求读取或安装 `jetlinks-project-ui-cli`。
- 不要假设外部组件库中的组件在目标 workspace 存在。
- 不要把 `packages/components/src` 下“存在目录/文档”误判为 `@jetlinks-web/components` 根入口已公开；必须核验 `components.ts`。
- 不要在没有目标版本与相邻生产代码证据时新增 `@jetlinks-web/components/es/...` 深层导入。
- 不要在业务模块中重复手写 `@jetlinks-web/components` 或 `@jetlinks-web-core/components` 已提供的能力。
- 不要因为某个业务模块里有一个局部组件，就把它复制到另一个业务模块；先判断应复用共享包、项目级组件，还是沉淀为稳定公共能力。
- 如果没有复用现有能力，必须说明已核验的映射文档、导出入口、相邻页面和不满足原因。

## 自检清单

- 是否已区分 `@jetlinks-web/components` 共享基础组件层与 `@jetlinks-web-core/components` 项目级组件层。
- 是否从 `packages/components/src/components.md` 按需定位文档，并用 `components.ts` 核验根导出。
- 是否核验目标项目的实际依赖版本与相邻生产用法。
- 是否按任务类型读取了 `jetlinks-web-core` 的总索引和分类索引，并只打开了相关候选说明。
- 是否避免把深层源码路径当作稳定公共 API。
- 是否避免把 `jetlinks-project-ui-cli` 作为默认依赖或导入来源。
- 是否只借鉴了相似业务中的结构和交互节奏，而不是复制字段、接口或指标。
