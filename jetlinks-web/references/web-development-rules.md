# JetLinks Web Development Rules

本文件是 `jetlinks-web` 的核心入口文档。先读本文件，再按任务需要加载其他参考文档。

## 任务分类

- 页面实现或改造：列表页、详情页、弹窗页、配置页
- 仪表盘组件：`visDashboard` 运行组件、配置面板、设计器接线
- 能力复用：组件、hooks、utils、包级能力选择
- 目录落点：代码放 `jetlinks-web-core` 还是 `modules/*-ui`
- 状态治理：本地状态、路由状态、store、服务端状态边界
- 质量与类型：交付质量、TypeScript 风险控制

## 标准工作流

1. 先查看目标模块相邻页面，确认真实技术栈、命名、交互风格。
2. 先核验工作区事实，再写代码：导出入口、依赖包、模块目录、已有示例。
3. 先做能力复用评估，再决定是否新增实现。
4. 只加载最小必要参考文档，不一次性读取全部 references。
5. 使用最小完整改动完成需求，优先沿用现有页面组合和模块边界。
6. 按质量与类型约束做交付前自检，补充可验证路径。

## 按场景加载文档

- 能力复用与组件/Hook/utils 选型：[`capability-reuse-rules.md`](capability-reuse-rules.md)
- `visDashboard` 仪表盘组件开发：[`dashboard-component-rules.md`](dashboard-component-rules.md)
- 模块与文件落点：[`directory-structure-rules.md`](directory-structure-rules.md)
- 状态边界与 store 使用：[`state-management-rules.md`](state-management-rules.md)
- 质量与类型约束：[`quality-and-type-rules.md`](quality-and-type-rules.md)
- 示例查找入口：[`example-locations.md`](example-locations.md)
- 快速导航总览：[`index.md`](index.md)

## 核心约束

- 不要发明不存在的组件契约、hook 签名或 utils API。
- 不要绕开已有 `@jetlinks-web-core`/`@jetlinks-web` 能力重造同类实现。
- 不要把文档中的能力名称当作固定事实，必须以当前工作区导出为准。
- 不要在页面内硬编码路由权限、菜单元数据、API base 或 token 行为。
- 不要把一次任务扩展成大范围结构重写，优先最小改动、可验证交付。

## 自检清单

- 是否已核验目标能力在当前工作区真实存在。
- 是否优先复用了现有组件、hooks、utils 或 store 契约。
- 是否保持了模块边界、目录风格和页面交互一致性。
- 是否完成了关键交互、状态流、路由权限和类型风险验证。
