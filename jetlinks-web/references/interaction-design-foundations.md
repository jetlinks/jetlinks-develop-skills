# 交互设计依据与适用边界

维护技能、主任务 / 信息架构不明或整体体验反复修补时定点读取。标准规定可访问性底线，研究解释认知与操作，设计系统提供模式；没有统一标准规定企业页面必须采用几栏、几个卡片或“基本信息 / 操作 / 联动”三个 Tab。

## 文献如何改变设计选择

| 来源 | 可采用的判断 | 不能推导成 |
| --- | --- | --- |
| [Object-Oriented UX](https://alistapart.com/article/object-oriented-ux/) | 按用户理解的对象、内容和关系组织上下文导航，再对照任务安排动作 | 从数据库实体机械生成菜单，或要求新建本体后端 |
| Ant Design [Make it Direct](https://ant.design/docs/spec/direct/) / [Stay on the Page](https://ant.design/docs/spec/stay/) | 原位操作、局部展开减少同一任务的上下文切换，允许渐进修改和核对 | 所有字段自动保存、禁止弹窗，或为密集首次录入隐藏输入 |
| Ant Design [Proximity](https://ant.design/docs/spec/proximity/) / [Layout](https://ant.design/docs/spec/layout/) | 组内靠近、组间分开，使用共同对齐线、尺度和可伸缩空间 | 固定列数、硬抄外部间距，或靠补卡片 / 大标题填空 |
| NN/g [Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) / [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) | 状态可见、用户语言、识别优于回忆，低频细节按需出现，错误可恢复 | 主动作 / 必需字段藏进多级弹窗，或把点击越少当唯一标准 |
| NN/g [Icon Usability](https://www.nngroup.com/articles/icon-usability/) | 图标依赖经验，必要文字承担明确含义 | 所有选项加图标，或用 tooltip 替代标签 |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) 与 APG [Combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) / [Listbox](https://www.w3.org/WAI/ARIA/apg/patterns/listbox/) | 保持可读、焦点、键盘、可理解名称与选择语义 | 自称已经完整符合 WCAG，或只换视觉不处理真实宿主交互 |
| [INP](https://web.dev/articles/inp) | 观察交互到下一次绘制，区分本地反馈、远程等待与最终完成 | 将现场第 75 百分位不高于 200ms 的良好阈值当接口 SLA 或一次点击验收 |

业务语义、提交边界与页面组合是结合平台契约的工程判断，不冒充文献逐字结论。设计系统的视觉例子不能证明目标组件可用；平台源码和已接受交互决定具体接入方式。新增依据只补会改变选择的部分，不要求普通任务阅读全文或查完所有案例。

## 轻量外观仍需可用

- 必要标签与帮助不能只剩 placeholder / hover；弱化用层级、字重和间距，普通文本按 WCAG 1.4.3 AA 保持至少 4.5:1，大文本至少 3:1，不要求装饰文字全部同权。
- 焦点可见且不被自建固定区完全遮挡（2.4.7 / 2.4.11）；图标有可访问名称，指针目标按 2.5.8 AA 的 24×24 CSS px 或条款例外核对，图标绘制尺寸不等于点击范围。
- 拖动之外保留适用的单指针替代，并支持键盘；常用操作不能只在鼠标 hover 时出现。复用控件既有语义，不逐业务手写另一套键盘状态机。
- 按 [Reflow 1.4.10](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) 检查窄宽度 / 放大后的内容和动作；二维数据表等按条款例外处理，横滚限定在需要比较的区域，不让整个页面溢出。
- 状态与错误可理解且不只靠颜色；适用状态消息可被辅助技术获知（4.1.3），不为每次采样更新强制抢焦点或播报。

## “直观、现代、顺滑”的证据

| 目标 | 阶段末观察 |
| --- | --- |
| 直观 | 能否找到第一步，分清当前对象、事实、配置和可执行动作；记录误选、求助与任务完成情况 |
| 连续可控 | 同一任务的切页 / 弹窗、重复选择和输入是否必要；返回、取消及失败后能否恢复上下文 |
| 清晰协调 | 正式壳层中标题、内容、动作有层级；长文本、密集数据和窄容器仍能阅读与操作 |
| 顺滑 | 本地反馈是否及时，焦点 / 布局是否稳定；远程等待可理解，旧结果不覆盖当前输入 |

只报告实际证据：源码核对、规则走查、浏览器技术验证、真实用户任务观察是不同强度。没有用户或运行测量时，不将截图、结构校验或设计偏好写成效率和可用性提升的实证。
