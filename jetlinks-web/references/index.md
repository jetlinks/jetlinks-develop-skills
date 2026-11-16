# JetLinks Web References Index

本文件仅做按需导航。任务入口与局部改动路径在 [SKILL.md](../SKILL.md)；不需要按序阅读此表。

## Navigation

- [web-development-rules.md](web-development-rules.md): 核心入口、任务分类、标准工作流与核心约束
- [component-source-rules.md](component-source-rules.md): `@jetlinks-web/components` 共享基础组件与 `@jetlinks-web-core/components` 项目级组件的双事实源、外部参考边界
- [core-capability-docs.md](core-capability-docs.md): `jetlinks-web-core` 组件、hooks、utils、store 与页面说明的按需读取和核验顺序
- [component-reuse-patterns.md](component-reuse-patterns.md): 卡片、列表、详情、图标、动态编辑、抽屉、标签等场景的双层组件复用矩阵
- [capability-reuse-rules.md](capability-reuse-rules.md): 组件/hooks/utils 与包级能力复用规则
- [code-organization-rules.md](code-organization-rules.md): 函数封装、设计模式、组件边界、Props/Emits 契约与职责抽离流程
- [dashboard-component-rules.md](dashboard-component-rules.md): `visDashboard` 仪表盘组件目录、注册、分层与接线规则
- [directory-structure-rules.md](directory-structure-rules.md): 目录层级与模块落点规则
- [page-pattern-decision-rules.md](page-pattern-decision-rules.md): 根据业务目标选择 CRUD、工作台、详情页、分步流等页面分型
- [semantic-ui-design-rules.md](semantic-ui-design-rules.md): 基于对象语义与用户任务规划企业菜单、列表、详情分组、业务联动、规则 / 流程及配置；区分标准、设计方法与项目规则
- [task-interaction-rules.md](task-interaction-rules.md): 从表单设计器、数采、指标模板、属性预处理提炼连续任务、内容操作、语义控件、草稿与结果联动，约束表单感、分散交互和原型验收
- [shared-interaction-contracts.md](shared-interaction-contracts.md): 公共选项、就地编辑、面板、任务草稿与试验反馈的统一契约、分层和验收；扩展现有能力，保留业务编辑器语义
- [interaction-design-foundations.md](interaction-design-foundations.md): 直接操作、Nielsen 原则、Ant Design、Carbon、WCAG / APG 与响应性能的文献依据、适用边界和任务体验评估
- [block-admission-rules.md](block-admission-rules.md): 判断统计卡、图表、快捷入口、概览区等区块是否值得存在
- [business-ui-example-rules.md](business-ui-example-rules.md): 如何借鉴相似业务案例，以及哪些“看起来高级”的设计不应照搬
- [condition-filter-rules.md](condition-filter-rules.md): 表达式搜索、Token 化条件输入、远程选项面板、条件路由与快捷筛选联动规则
- [enum-rendering-rules.md](enum-rendering-rules.md): 后端 `EnumDict` / `I18nEnumDict` 返回 `{ value, text }` 时的显示、提交、筛选和回显规则
- [state-management-rules.md](state-management-rules.md): 状态边界与 store 使用规则
- [quality-and-type-rules.md](quality-and-type-rules.md): 质量约束与 TypeScript 约束
- [example-locations.md](example-locations.md): 示例定位与检索命令

## Quick Selection

1. 新页面、主交互或业务体验设计：`web-development-rules.md`
2. 选择或新增组件时确认相应组件事实源和外部参考边界：`component-source-rules.md`；涉及共享基础组件时，从当前 workspace 的 `packages/components/src/components.md` 按需打开单组件文档
3. 涉及 core 公共能力时，按 `core-capability-docs.md` 读取总索引和对应分类 README，再核验真实导出与生产用法
4. 页面结构或交互路径有多种可能：用 `page-pattern-decision-rules.md` 分型并记录方案档案
5. 需要统一卡片、列表、详情、图标、动态编辑等组件：`component-reuse-patterns.md`
6. 页面结构仍不知道该做成什么：`page-pattern-decision-rules.md`
7. 不确定某个区块、统计卡或图表该不该存在：`block-admission-rules.md`
8. 需要借鉴案例但怕抄错场景：`business-ui-example-rules.md`
9. 需要表达式搜索、通用筛选或远程选项筛选：`condition-filter-rules.md`
10. 接口字段来自 `EnumDict` / `I18nEnumDict` 或返回 `{ value, text }`：`enum-rendering-rules.md`
11. 新增抽象或复用不明确时：`capability-reuse-rules.md`
12. 做 `visDashboard` 仪表盘组件：`dashboard-component-rules.md`
13. 不确定代码放哪里：`directory-structure-rules.md`
14. 状态边界不清晰：`state-management-rules.md`
15. 交付前质量或类型风险检查：`quality-and-type-rules.md`
16. 需要找真实实现样例：`example-locations.md`
17. 配置、设计器、规则 / 公式编辑，或用户反馈表单感重、操作分散、原型还原差：`task-interaction-rules.md`；只查控件时直接读其“控件按意图选择”节，不重做整页方案
18. 查询设计规范、整体体验评审、直观性与顺滑度取舍：`interaction-design-foundations.md`；只查相关依据，不将其作为所有前端改动的必读材料
