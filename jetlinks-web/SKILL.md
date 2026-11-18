---
name: jetlinks-web
description: 在 JetLinks Vue3 前端设计或实现页面、交互、组件与状态。局部修改直接沿现有契约，新页面按业务任务组织并复用平台组件。
---

# JetLinks Web

负责前端任务闭环、信息表达、组件职责及状态。已定位的文案、prop 或样式调整直接修改，不为局部工作重做页面设计。

## 工作方式

1. 核验当前模块、相邻实现及本次所需组件 / 接口事实，保留用户已明确的目标与交互选择。
2. 新页面或主路径变化读 [页面设计](references/web-development-rules.md)，按未决问题选择语义或页面分型细则；已有合理方案与实施授权就继续。事实先查代码与接口，仅对仍影响业务含义、保存范围或主要路径的未决事项询问。
3. 能力选型按 [复用规则](references/capability-reuse-rules.md) 从相关锚点核验，找到适用能力即停止扩搜；职责或抽象变化再查 [代码组织](references/code-organization-rules.md)。
4. 沿用 Vue 3 SFC、`script setup lang="ts"`、组件库和样式 token；阶段末按实际改变的交互、类型与状态风险集中验证。

跨页面共享契约、前后端状态链路或公共能力替换发生实质变化时，集成收尾按 [任务整体审查](../jetlinks-review/references/review-method.md#任务整体审查) 核对累计结果与受影响消费者；局部文案、prop 或样式调整沿当前范围验证。

## 按需细则

| 当前动作 | 读取 |
| --- | --- |
| 核实组件 API / 导出 | [组件事实源](references/component-source-rules.md)；core 能力不明再查 [分类文档](references/core-capability-docs.md) |
| 菜单 / 分区语义未明，内容平铺或顶部说明挤占主区 | [业务语义、信息重心与密度](references/semantic-ui-design-rules.md) |
| 控件选型、尺寸、密度或搭配不协调 | [选择与搭配](references/component-reuse-patterns.md#组件选择与搭配) |
| 按钮语义、轻量下拉、选择与选项内容 | [动作与选择](references/action-and-selection-rules.md) |
| 详情、原位编辑、分区、侧栏、列表及整页组合 | [场景组件](references/component-reuse-patterns.md) |
| 设计器、联动配置、公式 / 规则编辑或交互分散 | [连续交互](references/task-interaction-rules.md)；整体体验的依据缺口再查 [设计依据](references/interaction-design-foundations.md) |
| 通用条件搜索、远程选项与路由编解码 | [ConditionFilter](references/condition-filter-rules.md) |
| 后端 EnumDict / I18nEnumDict | [枚举渲染](references/enum-rendering-rules.md) |
| 状态归属、重叠请求或生命周期 | [状态管理](references/state-management-rules.md) |
| 业务页面增加告警、公式 / 指标计算或通知配置 | [平台能力复用](../jetlinks-boundary/references/platform-capability-reuse-rules.md)：先核验配置 / 管理契约与公开组件，不另造整套平台管理功能 |
| 类型、注释、视觉 token 或质量风险 | [质量规则](references/quality-and-type-rules.md) |
| 新目录 / 模块，或仪表盘注册 | [目录落点](references/directory-structure-rules.md) 或 [Dashboard](references/dashboard-component-rules.md) |
| 统计 / 图表区块，或借鉴外部案例 | [区块准入](references/block-admission-rules.md) 或 [案例边界](references/business-ui-example-rules.md)；找真实样例再读 [定位](references/example-locations.md) |

## 关键边界

- `@jetlinks-web/components` 是基础层，`@jetlinks-web-core/components` 是项目层；实际导出证明可用性，一层文档不能证明另一层。优先既有 props、slots、schema 和项目封装，不复制控件或深导入其他业务模块私有实现。
- 按业务任务组织导航与信息重心，既有组件及 token 提供视觉基线。阅读、录入与业务动作分清；信息页选择优先轻量表达，保留必要名称、选择能力和提交语义。
- 展示组件不暗含 API、全局状态写入或业务编排；按职责拆分，不按行数 / 文件数强拆。通用组件缺陷须 [回 owner 修复并提交 PR](../jetlinks-conventions/references/root-cause-and-no-hack-rules.md#通用组件缺陷的闭环)，不能用业务包装或页面特调绕过。
- 通用搜索复用现有 ConditionFilter 及编码链；枚举展示用 `text`，提交与比较用 `value`。i18n、权限、路由与设计 token 沿用平台机制。
- 原型说明、TODO、开发过程和无关内部标识不进入成品 UI；图表和数字有真实来源及用户用途。

说明实际变化、关键决定与验证；局部修改可一两句交付。更细入口见 [索引](references/index.md)，无需依次阅读。
