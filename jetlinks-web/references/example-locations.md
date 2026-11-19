# JetLinks 前端真实实现定位

仅在需要真实样例或尚未定位能力时读取。优先当前模块与仍有效的同类实现；案例用途与借鉴边界见 [业务案例](business-ui-example-rules.md)，导出与版本见 [事实源](component-source-rules.md)。

## 工作区入口

路径是候选，以当前构建别名、入口及模块布局为准；找到相关实现即停止扩搜，不按此表逐项读取。

| 需要 | 候选 |
| --- | --- |
| 业务页面、API 与状态 | modules/*-ui 的 views、api、hooks、store 等实际目录 |
| 公共组件、hooks、utils 与 store | jetlinks-web-core/src 下对应分类与公开入口；索引导航见 [能力文档](core-capability-docs.md) |
| 页面壳、路由与扩展加载 | core views、模块 index.ts / register.ts 与 module-registry.ts |

## 交互核对锚点

| 问题 | 工作区候选与用途 |
| --- | --- |
| 输入 / 计算 / 输出与试验 | core src/components/Metric/template/TemplateDesigner.vue；rule-engine UI views/MetricTemplate/index.vue，借连续配置与结果联系，不照搬完整画布 |
| 业务语句、表达式与阶段试算 | device UI views/device/components/PropertyRules/，输入范围沿真实预处理契约 |
| 阅读 / 编辑与分区 | core InlineEditForm、PlatformSettings、Expression、SelectOption、EqualHeightColumns 的实际契约 |
| 摘要与返回 | core DetailHeader、DetailMetaItem、PageChrome、PageBack 及已接入详情，核对职责，不复制局部像素 |
| 可扩展对象总览 | core ObjectOverview 的授权数据、能力装配与运行时；通用回退分区不替代业务信息架构 |
| 隔离交互演示 | core src/views/interaction-examples/ 与 semantic-scenarios.md；本地任务组合不证明生产服务接通 |

表单设计器、数采等只有独立预览时，先核验定义和接入；借内容、编辑与结果的联系，不把原型接口当生产公共能力。

## 跨模块资源

运行时模块能力沿已有 moduleRegistry 注册与读取契约协作，不深导入其他业务模块私有 API、hooks 或组件。源码候选为 core src/utils/module-registry.ts，公共别名与实际解析目标一致后再使用。

提供方从模块 index.ts / register.ts 的 register 接入，消费者核验 getResource / getResourceItem 及真实类型；稳定共享类型、纯工具和 core 公共能力可直接从公开入口导入，不为每个函数新增运行时注册。不能仅凭此文中的方法名推断目标版本参数。

必要时用 rg 定点检索已知符号及调用方；不为满足样例数量扫描全部模块。
