# JetLinks 前端能力复用

用于组件 / hook / util 选型或新增公共能力。实际导出与版本归 [事实源](component-source-rules.md)，抽象边界归 [代码组织](code-organization-rules.md)。

## 选型与扩展

1. 从当前符号、导入或相邻有效实现定位，核验用途、公开 API 与目标版本；找到适用能力即停止扩搜。
2. 优先既有 props、slots、schema 和项目封装；组件组合查 [场景组件](component-reuse-patterns.md)，不重复手写已有按钮、输入、菜单、选择器和弹层。普通 div / section 布局不属于另造控件。
3. 不满足需求时，区分误用 / 装配、版本问题、公共缺陷、能力缺口和业务差异。确认公共缺陷按 [owner 修复与 PR](../../jetlinks-conventions/references/root-cause-and-no-hack-rules.md#通用组件缺陷的闭环) 处理；合法配置 / 扩展不因外观不同被误判为规避。
4. 新抽象须有独立职责或稳定复用价值；相似外观不证明同语义，单一消费者也不禁止合理边界。不建空 wrapper、万能组件或无职责透传链。

## 重点能力

- 组合条件搜索优先复用 ConditionFilter 及编解码链；固定筛选与旧页改动按 [筛选选型](condition-filter-rules.md#选型与条件-owner) 判断。
- 公式编辑 / 查看核验 core Expression 的 MathExpressionEditor、MathExpressionView 等公共入口，复用 MathLive 与结构化表达式；指标、试算和执行职责见 [计算复用](../../jetlinks-boundary/references/platform-capability-reuse-rules.md#计算先选结果能力再选公式表达)。
- 运行时扩展核验 RegistryComponent、RemoteComponent 与 moduleRegistry 的实际注册 / 加载契约；稳定共享类型、纯工具可用其公共静态入口，不一律运行时注册。
- 告警、计算和通知的业务接入复用 [平台能力](../../jetlinks-boundary/references/platform-capability-reuse-rules.md)，不从页面另造整套管理系统。

## Hook、工具与 Store

锚点不足时按 [分类文档](core-capability-docs.md) 定位，不遍历全部目录：

| 需要 | 定位方向 |
| --- | --- |
| Tab 保存 / 返回、平台 Context、扩展选项与订阅 | 相关 hooks 及调用方 |
| 菜单 / 路由、API base、上传鉴权、反馈与下载 | 相关 utils / 服务；条件编解码在 ConditionFilter 契约确认 |
| 用户、菜单、权限与配置 | 已有 store / context，状态归属见 [状态管理](state-management-rules.md) |

非首屏、按需展示或较大组件沿现有分包策略加载；首屏关键和轻量同步组件可静态导入，不给所有组件机械套异步加载。布局使用公开组合和项目 token，不以 wrapper 或深层 CSS 修补公共缺陷。
