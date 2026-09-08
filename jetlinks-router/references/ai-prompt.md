# JetLinks 路由补充索引

日常入口是 [jetlinks-router](../SKILL.md)。本文件保留常见场景的最小组合与规则归属，供路由不明确时查阅；不复制各技能的执行流程，也不要求新任务先读本文件。

## 选择方法

围绕当前 decision question 和下一动作选择技能。新请求给出精确 symbol / changed path 时直接定位；只有实际发生压缩、暂停恢复或交接，才走 task-continuity 的 continuation fast path。已有正确路线和有效锚点时继续执行。

| 场景 | 当前需要的组合 | 后续边界出现时才补充 |
| --- | --- | --- |
| 已知实体字段按既有契约贯通 DTO 与 Controller | CRUD | 新增权限边界才加 assets-permission；跨层本身不触发复杂求解 |
| 查询结果受资产权限控制 | CRUD + assets-permission | 自定义跨边界调用出现时加 boundary |
| 生命周期变动产生领域副作用 | events | Mono / Flux 链路需要处理时加 reactive |
| 协议报文已有明确样例和目标字段 | protocol | 竞争根因或语义未决时由 systematic-solving 判定准入 |
| 查找 Command 的生产者与消费者 | code-navigation + JetLinks 导航扩展 | 改写交互方式时加 boundary |
| 已定位页面的一处文案 / prop / 样式 | web 的局部改动路径 | 仅加载实际改变的 copy、类型或组件契约规则 |
| 新页面或主交互承载变化 | web 的页面设计路径 | 有后端接口变化再加入其 owner |
| 长任务恢复或阶段状态可能过期 | task-continuity | Git / Trellis 适配确有需要时读恢复映射 |
| 多个已冻结契约、独立可验收的切片 | agent-orchestration | 由它选择实际协作模式、模型能力与验收 |
| 多种根因或修复反复失败 | systematic-solving | 准入后按实际链路加入领域技能 |

## 规则归属

- 复杂求解准入、语义分叉与证据预算：[systematic-solving](../../systematic-solving/SKILL.md)。
- 委派权限、总控职责、写集与结果接纳：[agent-orchestration](../../agent-orchestration/SKILL.md)。
- 原目标、持续约束、下一动作、恢复身份和证据有效性：[task-continuity](../../task-continuity/SKILL.md)。
- 检索能力选择、代码关系强度、目标语言和局部图范围：[code-navigation](../../code-navigation/SKILL.md)；JetLinks 关系见 [导航扩展](code-navigation-jetlinks-rules.md)。
- 后端任务契约、已有授权复用、按风险选测试：[后端设计与测试规则](backend-design-test-driven-rules.md)。
- 权威文档与临时运行态的落点：[制品归属](document-placement-rules.md)。
- 编码约定、兼容性、注释、i18n、追踪与运维：[conventions](../../jetlinks-conventions/SKILL.md)。
- 前端页面分型、组件和质量：[web](../../jetlinks-web/SKILL.md)。
- 分支、中文 Conventional Commit 与 PR：[delivery](../../jetlinks-delivery/SKILL.md)。

用户要求分析时交付可支撑当前决策的事实与未决项；要求实现时沿已明确目标推进到可验证结果。对状态询问简短作答后回到主线；不要因新一轮对话重新提问已解决的问题。

路由评测使用 `user_confirmation_required` 和 `unique_next` 等字段，定义与用例见 [evaluation-cases](evaluation-cases.md)。字段是工具接口，不是普通回答的固定模板。
