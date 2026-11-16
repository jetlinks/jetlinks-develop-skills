---
name: jetlinks-web
description: 在 JetLinks Vue3 前端实现或改造页面、交互、组件、状态与类型。适用于对象工作区、可视化配置、连续规则编辑、列表 / 详情、条件筛选和运行时扩展；围绕业务任务组织就地操作与验证反馈，避免传统全量表单和分散操作，按当前工作区导出复用能力。
---

# JetLinks Web

从本次实际变化选择路径。已定位的一处字段、prop、文案或样式调整，可以直接沿相邻实现修改；不必重新设计页面、扫描全部复用层或为未改逻辑补说明。

## Workflow

1. 保留用户已明确的目标、限制和交互选择，确认当前模块及相关代码锚点。只补当前修改需要的组件导出、接口、i18n 或状态事实。
2. 新页面、页面壳层、信息架构或主筛选 / 主列表 / 主详情承载发生变化时，读 [页面分型](references/page-pattern-decision-rules.md)，根据真实用户任务形成方案档案。菜单规划、跨业务或整体风格设计先按 [业务语义与交互表达](references/semantic-ui-design-rules.md) 区分对象、属性、关系、动作和过程，再选择承载。表单与详情的持续维护、配置、设计器或表单感 / 分散交互问题，结合 [任务连续交互](references/task-interaction-rules.md)。已知事实支持一个方案且用户要求实施时采用并继续；只有影响契约或主要操作路径的关键未决选择才询问。
3. 新增组件 / hook / util 或改变职责边界时，读 [能力复用](references/capability-reuse-rules.md) 与 [代码组织](references/code-organization-rules.md)。从相关锚点和相邻实现查起，找到可信能力即停止扩搜；复用不合适时说明实际缺口，按职责拆分，不按行数拆分。
4. 只加载下表中当前动作需要的 references。实现最小完整变化，保留 Vue 3 SFC + `script setup lang="ts"` 及相邻代码约定。
5. 在连贯阶段结束后，按改变的可观察行为、类型与交互风险集中验证。复用有效证据，报告真实未覆盖风险；不以固定检查清单制造无关构建、注释或抽象。

## Conditional References

| 当前任务 | 读取 |
| --- | --- |
| 企业菜单、台账 / 详情、业务联动、规则 / 流程或设置的整体设计 | [业务语义与交互表达](references/semantic-ui-design-rules.md)，先分清身份、属性、引用、关系、事实、动作与过程，再定分组和主次 |
| 新页面、主交互或业务体验设计 | [页面分型](references/page-pattern-decision-rules.md)、[页面设计规则](references/web-development-rules.md)；选择组件时再查 [场景矩阵](references/component-reuse-patterns.md) |
| 配置 / 设计器 / 规则编辑，表单感重、操作分散或原型还原 | [任务连续交互](references/task-interaction-rules.md)；找实际组件时查 [示例定位](references/example-locations.md) |
| 下拉 / 级联 / 菜单等候选项呈现 | [选项视觉层级](references/task-interaction-rules.md#下拉与候选项的视觉层级)；优先语义图标、主名称与弱化短说明，选中值保持紧凑 |
| 查询设计文献 / 行业规范、整体体验评审或设计取舍有争议 | [交互设计依据与评估](references/interaction-design-foundations.md)，区分标准要求、可用性原则与项目选择，不机械套固定布局 |
| 选择 / 新增组件，核对包导出 | [组件事实源](references/component-source-rules.md)；涉及 core 时按 [能力文档](references/core-capability-docs.md) 定位相关分类 |
| 新增抽象、复用不明确或职责变化 | [能力复用](references/capability-reuse-rules.md)、[代码组织](references/code-organization-rules.md) |
| 跨模块交互一致性、原型嵌入不协调、公共组件评审或扩展 | [公共交互契约](references/shared-interaction-contracts.md)；先核对宿主壳层、主题环境与组件变体，再统一选项、编辑、面板和反馈行为 |
| 通用搜索、token 条件、远程选项、路由编解码 | [ConditionFilter](references/condition-filter-rules.md) |
| EnumDict / I18nEnumDict 或 `{ value, text }` 字段 | [枚举渲染](references/enum-rendering-rules.md) |
| 类型、复杂注释、样式 token 或质量风险 | [质量与类型](references/quality-and-type-rules.md) |
| 状态 / 生命周期 / 路由归属变化 | [状态管理](references/state-management-rules.md) |
| 详情轻量编辑、反向引用、侧栏、PageHead 或浮动操作 | [场景组件与整页约定](references/component-reuse-patterns.md) |
| 表单 / 详情的读写一体、配置、左右分区或自适应 | [任务连续交互](references/task-interaction-rules.md#表单与详情的读写一体)、[Core 自包含场景](references/example-locations.md)，按当前任务读取对应示例 |
| 新目录或模块落点 | [目录结构](references/directory-structure-rules.md) |
| 仪表盘运行组件 / 配置 / 注册接线 | [Dashboard](references/dashboard-component-rules.md) |
| 添加指标、图表或其他信息区块 | [区块准入](references/block-admission-rules.md) |
| 借鉴其他页面或寻找真实例子 | [业务参考](references/business-ui-example-rules.md)、[示例定位](references/example-locations.md) |

更多细分入口见 [索引](references/index.md)，按需查阅，不将它作为必读链。

## 规则归属与技能并用

JetLinks 前端以本技能为入口：页面模式与是否需要用户选择由 [页面分型](references/page-pattern-decision-rules.md) 决定；任务路径、编辑与提交语义由 [任务连续交互](references/task-interaction-rules.md) 决定；状态放置见 [状态管理](references/state-management-rules.md)，组件可用性见 [组件事实源](references/component-source-rules.md)，抽象边界见 [代码组织](references/code-organization-rules.md)，通用查询行为见 [搜索规则](references/condition-filter-rules.md)。场景矩阵与示例仅帮助选择，不另立确认门槛、保存规则或固定布局。

同宿主仍安装旧版 `jetlinks-web-style` 时，将其视为兼容入口，方案选择收敛到本技能，不叠加旧目录中的固定密度、布局配额或重复确认流程。`frontend-design` 仅在明确需要视觉方向时补充建议，沿用户 brief 和项目设计系统，不因“现代化”自动更换字体、品牌色或页面骨架。发现同名技能副本规则不一致时先报告来源差异，修改权威来源，不把两个版本合并执行；安装同步按用户授权处理。

## Domain Constraints

- 组件 API 以当前工作区实际导出为准。`@jetlinks-web/components` 是跨项目基础层，`@jetlinks-web-core/components` 是项目层；验证使用到的层，不能用其中一层的文档证明另一层可用。共享层从 `packages/components/src/components.md` 定位，并用 `components.ts` 核验根导出；项目层核验 `jetlinks-web-core/src/components/index.ts`。已验证且未失效的导出可复用。
- 现有组件的 props、slots、config、schema 能覆盖需求时优先配置；已有稳定业务、权限、i18n 或路由约定的项目封装优先。不要复制基础控件、深导入其他业务模块私有代码或为缩短文件建立空包装。
- 表单、详情与配置围绕对象、内容、语句或关系展开：阅读与编辑沿同一内容布局，突出名称、关键状态与业务分区；新建直接激活关键输入。选择须改变实际内容，创建、配置、应用与详情沿同一对象接续，结果可回到原内容核对。分区、图标与卡片服务关系和操作，不为消除表单感制造空面板、隐藏入口或虚假选择。独立字段可轻量编辑，联动配置按完整草稿校验与提交；不按后端实体拆散任务，也不把长表单改成多个弹窗或单项保存。
- 用户已接受的原型决定当前改造范围内的操作路径；平台统一 token、尺寸、组件与语义反馈，不以复用旧页为由恢复旧流程。图标、颜色、选中和异常按统一语义区分，控件简化仍须保留可发现性、键盘操作与明确反馈。
- 页面 / container、展示组件、composable、service / API、util 按职责分工。展示组件不直接请求 API、写全局状态或暗含业务编排；本次不改变的相邻逻辑不因文件被触碰而强制重构。
- 通用搜索优先当前工作区的 ConditionFilter 及其路由编解码链。字段先用通用编辑类型与 transform hooks 表达；ProSearch 的适用边界见其 [规则](references/condition-filter-rules.md)，相邻页面用了它不等于新页面默认。
- 后端枚举对象显示 `text`，提交、筛选、比较和状态色使用 `value`；不直接渲染对象或复制后端文案映射。
- 使用 Ant Design / Ant Design Vue、现有组件和样式 token；需求未改变视觉体系时沿用它。布局由真实业务任务决定；指标 / 图表必须有业务用途和数据来源，原型标注、TODO 和开发过程说明不进入成品 UI。
- 文案与 i18n 沿用当前工作区机制。面向实际用户写内容：开发集成者需要的 API 路径、Topic 或命令 ID 可以准确展示；无关内部标识和设计说明不展示。对已有明确语义的局部文案修改，不重问整页角色。
- 新增或实质修改的公共函数、业务规则、状态联动、兼容、并发和生命周期逻辑按 [质量规则](references/quality-and-type-rules.md) 补简洁注释；明显代码不逐行复述，未改逻辑不触发逐文件“无需注释”说明。

复杂问题是否需要系统求解，统一使用 [systematic-solving Admission](../systematic-solving/SKILL.md#admission)，不以跨 API / route / state 层或出现 retry / mock 词汇自行升级。命名、i18n、追踪等需要跨端规范时再加入 [conventions](../jetlinks-conventions/SKILL.md)；提交或 PR 请求加入 [delivery](../jetlinks-delivery/SKILL.md)。

## Response

说明实际变化、关键决策和验证结果；只报告当前任务涉及的方案、复用缺口、条件搜索、枚举或剩余风险。局部修改可以用一两句话交付，无需复述未触发的路径。
