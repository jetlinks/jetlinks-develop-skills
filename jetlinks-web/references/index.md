# JetLinks Web References Index

本文件仅做轻量导航。核心入口是 [`web-development-rules.md`](web-development-rules.md)。

## Navigation

- [web-development-rules.md](web-development-rules.md): 核心入口、任务分类、标准工作流与核心约束
- [component-source-rules.md](component-source-rules.md): `@jetlinks-web/components` 共享基础组件与 `@jetlinks-web-core/components` 项目级组件的双事实源、外部参考边界
- [component-reuse-patterns.md](component-reuse-patterns.md): 卡片、列表、详情、图标、动态编辑、抽屉、标签等场景的双层组件复用矩阵
- [capability-reuse-rules.md](capability-reuse-rules.md): 组件/hooks/utils 与包级能力复用规则
- [code-organization-rules.md](code-organization-rules.md): 函数封装、设计模式、组件边界、Props/Emits 契约与职责抽离流程
- [dashboard-component-rules.md](dashboard-component-rules.md): `visDashboard` 仪表盘组件目录、注册、分层与接线规则
- [directory-structure-rules.md](directory-structure-rules.md): 目录层级与模块落点规则
- [page-pattern-decision-rules.md](page-pattern-decision-rules.md): 根据业务目标选择 CRUD、工作台、详情页、分步流等页面分型
- [block-admission-rules.md](block-admission-rules.md): 判断统计卡、图表、快捷入口、概览区等区块是否值得存在
- [business-ui-example-rules.md](business-ui-example-rules.md): 如何借鉴相似业务案例，以及哪些“看起来高级”的设计不应照搬
- [condition-filter-rules.md](condition-filter-rules.md): 表达式搜索、Token 化条件输入、远程选项面板、条件路由与快捷筛选联动规则
- [state-management-rules.md](state-management-rules.md): 状态边界与 store 使用规则
- [quality-and-type-rules.md](quality-and-type-rules.md): 质量约束与 TypeScript 约束
- [example-locations.md](example-locations.md): 示例定位与检索命令

## Quick Selection

1. 先明确任务类型和执行路径：`web-development-rules.md`
2. 先确认双层组件事实源和外部参考边界：`component-source-rules.md`；涉及共享基础组件时，从当前 workspace 的 `packages/components/src/components.md` 按需打开单组件文档
3. 页面结构或交互路径有多种可能：用 `page-pattern-decision-rules.md` 分型并记录方案档案
4. 需要统一卡片、列表、详情、图标、动态编辑等组件：`component-reuse-patterns.md`
5. 不确定某个区块、统计卡或图表该不该存在：`block-admission-rules.md`
6. 需要借鉴案例但怕抄错场景：`business-ui-example-rules.md`
7. 需要表达式搜索、通用筛选或远程选项筛选：`condition-filter-rules.md`
8. 先判断复用能力再写代码：`capability-reuse-rules.md`
9. 做 `visDashboard` 仪表盘组件：`dashboard-component-rules.md`
10. 不确定代码放哪里：`directory-structure-rules.md`
11. 状态边界不清晰：`state-management-rules.md`
12. 交付前质量或类型风险检查：`quality-and-type-rules.md`
13. 需要找真实实现样例：`example-locations.md`
