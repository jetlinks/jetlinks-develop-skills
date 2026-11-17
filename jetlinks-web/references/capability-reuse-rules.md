# JetLinks 前端能力复用

用于组件 / hook / util 选型或新增公共能力。页面骨架由 [页面设计](web-development-rules.md) 决定，函数和组件边界由 [代码组织](code-organization-rules.md) 决定。

## 最短选型路径

1. 从当前字段、组件或相邻生产用法查找，核实语义、公开 API、真实导出与目标版本；找到可信能力即停止扩搜。
2. 优先现有 props、slots、config / schema 或稳定的项目封装，再考虑增加公开能力。基础层和项目层的事实源见 [组件核验](component-source-rules.md)。
3. 不满足需求时，先区分误用 / 版本问题、组件缺陷、通用能力缺口和业务差异。确认缺陷必须在组件 owner 修复并提交 PR，按 [修复闭环](../../jetlinks-conventions/references/root-cause-and-no-hack-rules.md#通用组件缺陷的闭环)，不能以“无法复用”为由重新手写一套。
4. 仅在确有独立职责、状态或稳定消费者时抽取；单一消费者不禁止合理边界，多处相似也不强制合并。

## 组件与平台能力

以下是检索候选，不证明目标工作区已经导出；参数与交互以源码为准：

| 用途 | 候选与应核验的契约 |
| --- | --- |
| 整页、分区与对象呈现 | FullPage、EntityCard、CardBox、SectionCard、KvGrid、TabsCard；壳层、状态、选中与密度 |
| 列表与批量动作 | j-pro-table、VirtualScroll、BatchImport；数据请求、分页、选择、导入反馈 |
| 通用条件搜索 | ConditionFilter 及条件 / 路由编解码；字段、远程选项、回显见 [专用规则](condition-filter-rules.md) |
| 详情编辑与动作 | InputEditable、Editable、FormItemEditable、EditDialog、JlDrawerShell、StickyActionBar；保存、取消、校验与返回 |
| 分类 / 状态 / 资源选择 | MetaChip、ChipGroup、AppTag、MarketplaceResourcePicker、CardSelect；图标语义、选项与确认 |
| 可配置公式与查看 | core Expression 的 MathExpressionEditor、MathExpressionView；复用 MathLive 封装，宿主声明引用 / 函数目录，保存平台结构化表达式；执行与指标选型见 [计算复用](../../jetlinks-boundary/references/platform-capability-reuse-rules.md#计算先选结果能力再选公式表达) |
| 运行时扩展 | RegistryComponent、RemoteComponent；注册、code、插槽与组件加载契约 |

组件矩阵与整页组合只在确需设计时查 [场景组件](component-reuse-patterns.md)。不要手写库中已有的按钮、输入、菜单、选择器和弹层；普通 div / section 等布局语义不属于重复造控件。卡片选择根节点沿组件实际选择 / 事件契约，不为视觉包裹破坏交互。

## Hook、工具与 Store

需要 core 能力且锚点不足时，按 [分类文档](core-capability-docs.md) 定位相关 README、导出与生产用法，不读取全部分类：

- Tab 保存 / 返回、平台 Context、注册扩展节点：查 hooks。
- 菜单 / 路由、统一 API base、上传鉴权、提示去重、资源下载及纯转换：查 utils。
- 条件筛选编码 / 解码在 ConditionFilter 契约中确认，不假设位于公共 utils。
- 全局用户、菜单、权限与配置查 store；单页输入和草稿不全局化。状态生命周期见 [状态管理](state-management-rules.md)。

已有平台机制优先，禁止散落硬编码 API、token、菜单权限或重复请求逻辑。

## 新增与加载

- 相同语义且差异可由配置 / props / slots 表达时，复用或提炼正确 owner；仅视觉相似、权限 / 生命周期不同的结构保留各自职责。
- 公开契约、独立生命周期或复杂阶段可合理拆分；不因行数、重复次数或“以后可能”创造空 wrapper、巨型通用组件与参数透传链。
- 跨模块稳定能力放公开 core 入口；模块私有能力留业务模块。确认的通用组件缺陷不能伪装为局部业务封装。
- 非首屏、按需展示或较大的组件按现有分包方式懒加载；首屏关键和轻量同步组件可正常静态导入，不给所有组件机械套 defineAsyncComponent。
- 布局优先项目既有网格、列表、尺寸 token 和响应式策略；不能通过组件外壳或深层 CSS 修补通用组件内部缺陷。
