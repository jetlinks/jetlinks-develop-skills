# 交互设计依据与适用边界

维护技能、主任务 / 信息架构不明或整体体验反复修补时定点读取。标准规定可访问性底线，研究解释认知与操作，设计系统提供模式；没有统一标准规定企业页面必须采用几栏、几个卡片或“基本信息 / 操作 / 联动”三个 Tab。

## 文献如何改变设计选择

| 来源 | 可采用的判断 | 不能推导成 |
| --- | --- | --- |
| [Object-Oriented UX](https://alistapart.com/article/object-oriented-ux/) | 按用户理解的对象、内容和关系组织上下文导航，再对照任务安排动作 | 从数据库实体机械生成菜单，或要求新建本体后端 |
| Ant Design [Make it Direct](https://ant.design/docs/spec/direct/) / [Stay on the Page](https://ant.design/docs/spec/stay/) | 原位操作、局部展开减少同一任务的上下文切换，允许渐进修改和核对 | 所有字段自动保存、禁止弹窗，或为密集首次录入隐藏输入 |
| Ant Design [Proximity](https://ant.design/docs/spec/proximity/) / [Layout](https://ant.design/docs/spec/layout/) | 组内靠近、组间分开，使用共同对齐线、尺度和可伸缩空间 | 固定列数、硬抄外部间距，或靠补卡片 / 大标题填空 |
| Ant Design [Alignment](https://ant.design/docs/spec/alignment/) / [Repetition](https://ant.design/docs/spec/repetition/) | 同类内容保持可比较的对齐和稳定表达，重复的尺度与样式帮助识别结构 | 所有控件、文字和容器同尺寸，或拿某一组件库尺寸覆盖平台 token |
| Ant Design [Data Display](https://ant.design/docs/spec/data-display/) / NN/g [Visual Hierarchy](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/) | 按重要性、操作频率和关联程度安排呈现，用位置、尺度、对比与分组体现信息层级 | 所有字段等权平铺，或强制固定首屏数量、视觉扫描路径和同形卡片 |
| NN/g [Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) / [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) | 减少无关信息对注意力的竞争；状态可见、用户语言、识别优于回忆，低频细节按需出现，错误可恢复 | 一律删除顶部说明、隐藏必要风险 / 标签，把主动作 / 必需字段藏进多级弹窗，或把点击越少当唯一标准 |
| NN/g [Recognition and Recall](https://www.nngroup.com/articles/recognition-and-recall/) | 在当前操作处提供能识别的名称、内容与上下文，减轻记忆负担 | 所有信息常驻，或只用没有明确含义的图标替代文字 |
| NN/g [Icon Usability](https://www.nngroup.com/articles/icon-usability/) | 图标依赖经验，必要文字承担明确含义 | 所有选项加图标，或用 tooltip 替代标签 |
| Ant Design [Button](https://ant.design/components/button/) / [Dropdown](https://ant.design/components/dropdown/) | 用强调程度区分动作优先级，低频动作可收进菜单；名称和相邻上下文表明影响范围 | 每个操作都是主按钮、所有操作只剩图标，或按按钮名字固定样式 |
| Carbon [Dropdown](https://carbondesignsystem.com/components/dropdown/usage/) | inline 模式可在内容中降低选择器的表单感，当前值与名称仍可理解；检索需求影响选型 | 禁止所有 Select、删标签与焦点，或认为轻量动作菜单自动具备搜索 / 多选能力 |
| APG [Menu Button](https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/) / [Button](https://www.w3.org/WAI/ARIA/apg/patterns/button/) | 展开入口、执行动作与链接语义有别，沿正确宿主保留键盘、展开与焦点行为 | 只换外观就统一强加 menu 角色，或给业务页再造键盘状态机 |
| APG [Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) / [Window Splitter](https://www.w3.org/WAI/ARIA/apg/patterns/windowsplitter/) | 折叠与尺寸调节各有状态、被控区域和键盘语义；入口与内容关系可理解 | 折叠图标必须在搜索前、统一插槽顺序、所有详情都要侧栏，或示例尺寸成为通用断点 |
| WCAG [Consistent Identification](https://www.w3.org/WAI/WCAG22/Understanding/consistent-identification.html) | 相同功能保持一致的识别表达，名称仍反映上下文含义 | 同类字段一律失焦保存，或所有页面采用相同布局与提交语义 |
| Carbon [Forms](https://www.carbondesignsystem.com/building-blocks/core/patterns/forms) / [Data table](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines) | 表单适合录入，原位编辑适合上下文维护；字段帮助与错误可理解，列表集合动作、已选动作和单行动作各有对象范围 | 为去表单而隐藏首次输入，或照抄固定按钮数、表头带和批量工具栏外观 |
| Carbon [Text input](https://www.carbondesignsystem.com/building-blocks/core/components/text-input/guidelines) | 字段宽度与所需内容相称，按共同网格对齐；控件尺寸和文字层级作为组合核对 | 所有字段拉满剩余空间，或为了紧凑任意缩小控件和点击区域 |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) 与 APG [Combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) / [Listbox](https://www.w3.org/WAI/ARIA/apg/patterns/listbox/) | 保持可读、焦点、键盘、可理解名称与选择语义 | 自称已经完整符合 WCAG，或只换视觉不处理真实宿主交互 |
| [INP](https://web.dev/articles/inp) | 观察交互到下一次绘制，区分本地反馈、远程等待与最终完成 | 将现场第 75 百分位不高于 200ms 的良好阈值当接口 SLA 或一次点击验收 |

通用规则保留任务目标、选型条件和可验证结果；具体字段、布局、参数及入口位置不从单个案例提升为通用要求。业务语义、提交边界与页面组合是结合平台契约的工程判断，不冒充文献逐字结论。

平台组件文档拥有版本、API 和具体组合，业务案例只作按需定位或迁移验证；设计系统的视觉例子不能证明目标组件可用。新增依据只补会改变选择的部分，不要求普通任务阅读全文或查完所有案例。

## 轻量外观仍需可用

- 必要标签与帮助不能只剩 placeholder / hover；标签与可访问名称核对真实可操作节点，不能只看 Vue 已传入 prop。弱化用层级、字重和间距，普通文本按 WCAG 1.4.3 AA 保持至少 4.5:1，大文本至少 3:1，信息层级可以不同，但不通过低于适用对比要求的灰字表达次级内容。
- 焦点可见且不被自建固定区完全遮挡（2.4.7 / 2.4.11）；仅图标操作有真实可访问名称，随文字的装饰图标避免重复播报；指针目标按 2.5.8 AA 的 24×24 CSS px 或条款例外核对，图标绘制尺寸不等于点击范围。
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

维护技能或独立验证迁移能力时再读 [评测用例](evaluation-cases.md)。示例用于检验原则能否适应不同业务与约束，不作为普通设计任务的默认布局或预期答案。
