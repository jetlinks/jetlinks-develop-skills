# JetLinks 页面与交互设计

新页面、信息架构或主交互变化时读取。局部文案、prop、字段或样式调整沿已知契约处理，不重做方案或全域组件扫描。

## 从任务确定结构

确认用户当前要完成的任务、核心对象、必要动作与成功反馈。事实从代码、接口和已接受方案核验；只有仍未决且影响业务含义、保存范围或主要路径的事项才询问。呈现选择可用真实组件预览，不强制多方案、线框确认或独立方案文档。

- 业务任务决定入口与内容，不将服务、API 或数据库表平铺为菜单；菜单、详情分区和跨业务关系按 [业务语义](semantic-ui-design-rules.md) 组织。
- 页面类型未明时查 [页面分型](page-pattern-decision-rules.md)；它提供选择依据，不按业务名称固定布局。
- 列表、详情与概览围绕各自的判断建立 [信息重心](semantic-ui-design-rules.md#按任务建立信息重心)，避免字段等权平铺。统计、图表及快捷区的取舍见 [区块用途](block-admission-rules.md)。
- 设计器、联动配置与持续维护按 [连续交互](task-interaction-rules.md) 保留对象、修改与结果的联系；提交范围由业务依赖和接口决定。

## 页面组合与平台基线

使用当前正式壳层、组件库、字体、配色及 token。通用视觉指导用于改善比例、层级和阅读节奏；任务未包含整体视觉改版时，不另造品牌、hero 或动画体系。相邻旧页面也不能覆盖当前契约和已确认设计。

- 整页比例、侧栏、原位 / 分区编辑及自适应按 [场景组件](component-reuse-patterns.md)；同层尺寸与密度协调不等于所有控件等大。
- 按钮、信息页轻量选择与实际值录入按 [动作与选择](action-and-selection-rules.md) 区分；业务含义优先由 [界面组织与行为](semantic-ui-design-rules.md#界面表达与辅助说明) 表达，必要说明就近出现，不把页面做成功能讲解。
- 正式页面使用真实平台组件；独立预览不能证明完整宿主、权限或生产数据已接通。借鉴其他页面按 [案例边界](business-ui-example-rules.md)。

## 实现与阶段验收

- 选型按 [能力复用](capability-reuse-rules.md)，API / 导出按 [事实源](component-source-rules.md) 核验；找到适用能力即停止扩搜。确认的公共缺陷按 [owner 修复与 PR](../../jetlinks-conventions/references/root-cause-and-no-hack-rules.md#通用组件缺陷的闭环) 处理。
- 条件查询、枚举和前端状态分别归 [ConditionFilter](condition-filter-rules.md)、[枚举规则](enum-rendering-rules.md) 和 [状态管理](state-management-rules.md)，不在页面另造协议与事实源。
- 职责变化查 [代码组织](code-organization-rules.md)；类型、样式与验证范围按 [质量规则](quality-and-type-rules.md)。i18n、权限和路由继续使用平台机制。
- 阶段末按实际影响验证任务结果、必要的异常恢复、正式宿主及宽 / 窄容器，局部修改不扩成全系统重测。报告实际证据与未验证边界。

主任务未明或整体体验反复修补时，定点查 [设计依据](interaction-design-foundations.md)；已有明确合法的呈现偏好直接实施，不用调研重开已接受方案。标准、研究和设计系统用于解释取舍，不规定企业页面必须几栏或几个卡片。
