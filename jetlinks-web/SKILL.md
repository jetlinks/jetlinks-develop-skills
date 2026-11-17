---
name: jetlinks-web
description: 在 JetLinks Vue3 前端设计或实现页面、交互、组件与状态。局部修改直接沿现有契约，新页面按业务任务组织并复用平台组件。
---

# JetLinks Web

负责前端任务闭环、信息表达、组件职责及状态。已定位的文案、prop 或样式调整直接修改，不为局部工作重做页面设计。

## 工作方式

1. 核验当前模块、相邻实现及本次所需组件 / 接口事实，保留用户已明确的目标与交互选择。
2. 新页面、信息架构或主操作路径变化时，读 [页面分型](references/page-pattern-decision-rules.md) 和 [页面设计](references/web-development-rules.md)，按业务语义组织内容与动作。已有合理方案和实施授权就继续，只有改变主要操作路径的实质未决选择才询问。
3. 新增能力时从相关锚点按 [能力复用](references/capability-reuse-rules.md) 选型，找到可信组件即停止扩搜；只有职责或抽象发生变化时再查 [代码组织](references/code-organization-rules.md)。
4. 沿用 Vue 3 SFC、`script setup lang="ts"`、组件库和样式 token；阶段末按实际改变的交互、类型与状态风险集中验证。

跨页面共享契约、前后端状态链路或公共能力替换发生实质变化时，集成收尾按 [任务整体审查](../jetlinks-review/references/review-method.md#任务整体审查) 核对累计结果与受影响消费者；局部文案、prop 或样式调整沿当前范围验证。

## 按需细则

| 当前动作 | 读取 |
| --- | --- |
| 核实组件 API / 导出 | [组件事实源](references/component-source-rules.md)；core 能力不明再查 [分类文档](references/core-capability-docs.md) |
| 详情、原位编辑、分区、侧栏、列表及整页组合 | [场景组件](references/component-reuse-patterns.md) |
| 通用条件搜索、远程选项与路由编解码 | [ConditionFilter](references/condition-filter-rules.md) |
| 后端 EnumDict / I18nEnumDict | [枚举渲染](references/enum-rendering-rules.md) |
| 状态归属、重叠请求或生命周期 | [状态管理](references/state-management-rules.md) |
| 业务页面增加告警、计算或通知配置 | [平台能力复用](../jetlinks-boundary/references/platform-capability-reuse-rules.md)：先核验配置 / 管理契约与公开组件，不另造整套平台管理功能 |
| 类型、注释、视觉 token 或质量风险 | [质量规则](references/quality-and-type-rules.md) |
| 新目录 / 模块，或仪表盘注册 | [目录落点](references/directory-structure-rules.md) 或 [Dashboard](references/dashboard-component-rules.md) |
| 统计 / 图表区块，或借鉴外部案例 | [区块准入](references/block-admission-rules.md) 或 [案例边界](references/business-ui-example-rules.md)；找真实样例再读 [定位](references/example-locations.md) |

## 关键边界

- `@jetlinks-web/components` 是基础层，`@jetlinks-web-core/components` 是项目层；实际导出证明可用性，一层文档不能证明另一层。优先既有 props、slots、schema 和项目封装，不复制控件或深导入其他业务模块私有实现。
- 按对象、状态、关系和动作分区，读写围绕同一任务组织；不默认全量表单、散落弹窗或无关概览卡。左右分区、卡片、icon 与自适应服务业务重点，不为填满页面装饰。
- 展示组件不暗含 API、全局状态写入或业务编排；按职责拆分，不按行数 / 文件数强拆。通用组件缺陷须 [回 owner 修复并提交 PR](../jetlinks-conventions/references/root-cause-and-no-hack-rules.md#通用组件缺陷的闭环)，不能用业务包装或页面特调绕过。
- 通用搜索复用现有 ConditionFilter 及编码链；枚举展示用 `text`，提交与比较用 `value`。i18n、权限、路由与设计 token 沿用平台机制。
- 原型说明、TODO、开发过程和无关内部标识不进入成品 UI；图表和数字有真实来源及用户用途。

说明实际变化、关键决定与验证；局部修改可一两句交付。更细入口见 [索引](references/index.md)，无需依次阅读。
