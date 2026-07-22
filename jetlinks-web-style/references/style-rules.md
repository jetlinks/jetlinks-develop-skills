# JetLinks Web Style Rules

本文件约束 JetLinks 前端页面中自定义内容的样式实现。Ant Design Vue 组件自身的按钮、输入框、表格、弹窗、卡片、标签、表单、提示等样式优先完全遵循 Ant Design Vue 的组件规范和主题能力；只有业务自定义容器、自定义布局、自定义状态块、自定义卡片内容和局部补充样式，才优先复用目标前端 workspace 的 `jetlinks-web-core/src/style.css` 中的主题变量与 Tailwind 主题映射，不在业务组件里另起一套视觉体系。

## 样式来源优先级

1. 使用 Ant Design Vue 组件时，组件外观、状态、尺寸、表单、表格、弹窗、卡片、标签和提示默认按 Ant Design Vue 规范处理，不为了统一自定义 token 而覆盖组件内建样式。
2. 自己写的业务容器、布局、标题、说明、状态块、卡片内容、空态补充和局部样式，必须优先复用 `jetlinks-web-core/src/style.css` 已声明的 `--jet-theme-*`、语义别名、间距、字号、圆角、阴影和 Tailwind `jet-*` token。
3. 以下情况一定要使用 `style.css` token 或 Tailwind `jet-*` 原子类：页面壳层、卡片/列表/详情/表单/筛选/工具栏/Tab/抽屉/弹层中的自定义区域，任何可复用组件，任何业务状态色，任何文字层级、背景、边框、间距、圆角、阴影、focus ring、sticky 阴影、代码块配色。
4. 只有 SVG 坐标、canvas 计算、第三方样式 reset/兼容、组件内部无法抽象的单次几何微调可以写字面量；一旦同类值出现第二次，必须回到 `style.css` 补语义 token 或使用已有 token。
5. 优先参考目标模块相邻页面的布局节奏、class 命名和局部样式写法，保持同业务域一致，但相邻页面存在硬编码时不继续复制，应映射到 `style.css` token。
6. 页面级差异只写当前组件必要的 scoped 样式；多处稳定复用后才沉淀为公共变量、工具类或组件。
7. 自定义样式新增颜色、字号、圆角、阴影、间距前，必须确认 Ant Design Vue 组件能力与 `style.css` 现有变量无法覆盖。

## 变量分层

### 主题变量

`--jet-theme-*` 是全局主题源，适合承接项目主题、组件覆盖和跨模块稳定样式。

- `--jet-theme-primary`、`--jet-theme-primary-hover`、`--jet-theme-primary-active`：主按钮、主链接、选中态、关键操作和品牌强调。
- `--jet-theme-primary-soft`：主色浅背景、信息提示背景、选中卡片底色、轻量高亮区域。
- `--jet-theme-success`、`--jet-theme-warning`、`--jet-theme-error`：成功、警告、错误等业务状态色，优先用于状态点、Tag、Alert、Badge 或图标色。
- `--jet-theme-bg-base`、`--jet-theme-bg-layout`、`--jet-theme-bg-container`、`--jet-theme-bg-elevated`：页面底色、内容容器、卡片、浮层和弹出层背景。
- `--jet-theme-text-title`、`--jet-theme-text`、`--jet-theme-text-secondary`、`--jet-theme-text-description`、`--jet-theme-text-disabled`：标题、正文、辅助说明、描述和禁用文本。
- `--jet-theme-border`、`--jet-theme-border-secondary`：输入框/分割线/卡片边框与轻分割线。
- `--jet-theme-radius`、`--jet-theme-radius-lg`、`--jet-theme-radius-sm`：默认、较大、较小圆角。
- `--jet-theme-shadow`、`--jet-theme-shadow-secondary`：弹层/提升态阴影与普通卡片阴影。
- `--jet-theme-font-family`、`--jet-theme-stroke-width`：全局字体与基础描边宽度。

### 语义别名

`:root` 中的短变量用于业务组件快速表达语义，适合 scoped 样式和局部布局。新增业务样式优先使用这些语义名，只有主题接入、组件库覆盖或跨主题源配置才直接使用 `--jet-theme-*`。

- `--surface-page`：页面画布或工作区底色，通常用于页面根容器。
- `--surface-container`、`--surface-elevated`、`--surface-subtle`、`--surface-hover`：普通容器、浮起容器、浅强调背景、悬停背景。
- `--border-subtle`、`--border-strong`：常规边框和轻分割线，不要自行写新的灰色边框。
- `--text-primary`、`--text-secondary`、`--text-tertiary`、`--text-disabled`、`--text-placeholder`：标题/正文、辅助文本、弱化文本、禁用和占位文本。
- `--color-primary`、`--color-primary-text`、`--color-primary-soft`：主强调色、强调色上的文字、浅强调背景。
- `--color-success`、`--color-success-soft`、`--color-success-border`、`--color-warning`、`--color-warning-soft`、`--color-warning-border`、`--color-error`、`--color-error-soft`、`--color-error-border`、`--color-info`、`--color-info-soft`、`--color-info-border`：状态色、状态浅背景和状态边框。
- `--ambient-hero`、`--ambient-cool`、`--ambient-warm`：概览、头图区、空态或轻量装饰背景；普通表单和表格页不要滥用。
- `--code-dark-*`：代码块、脚本、日志或配置片段的深色展示区域。


## Token 决策门禁

只要本次实现会新增或修改自定义样式，先按下面顺序做决策，不能跳过：

1. 这个样式能否由 Ant Design Vue 或项目封装组件的 props、slots、size、status、type、variant、theme token 表达；能则不写自定义样式。
2. 这个样式是否属于页面语义或产品视觉语言；只要答案是“是”，必须使用 `style.css` token 或 Tailwind `jet-*` 原子类。
3. 这个样式是否只是一次性几何细节；只有 SVG 坐标、canvas 计算、第三方兼容、不可复用的局部修正可以写字面量。
4. 这个字面量是否已经在当前文件或相邻文件出现第二次；出现第二次就不再是局部修正，必须改用已有 token 或先补充公共语义 token。

### 变量选择速查

| 场景 | 首选 token | 什么时候用 | 不要用 |
| --- | --- | --- | --- |
| 页面根背景 | `--surface-page` / `bg-jet-bg-layout` | 页面最外层、工作区底色、内容区背板 | 直接写 `#f5f5f5`、灰阶字面量 |
| 普通内容容器 | `--surface-container` / `bg-jet-bg-container` | 卡片、列表容器、表单容器、详情主体 | 模块内自定义白色背景 |
| 浮层或提升容器 | `--surface-elevated` / `bg-jet-bg-elevated` | Popover、Dropdown 内容、浮起卡片、抽屉内容 | 用普通容器色再叠临时阴影 |
| 浅强调背景 | `--surface-subtle`、`--color-primary-soft` / `bg-jet-primary-soft` | 选中卡片、信息提示、轻量主色强调 | 大面积铺满普通表单/表格页 |
| hover 背景 | `--surface-hover` | 列表行 hover、可点击卡片 hover、轻量按钮 hover | 临时写 `rgba` 或灰色 hex |
| 主文本 | `--text-primary` / `text-jet-text` | 标题、正文、重要字段值 | 自定义黑色 hex |
| 次级文本 | `--text-secondary` / `text-jet-text-secondary` | 说明、副标题、辅助字段 | 用透明度降低主文本 |
| 弱文本/占位 | `--text-tertiary`、`--text-disabled`、`--text-placeholder` | 元信息、禁用、占位、空态弱提示 | 混用多套灰阶 |
| 常规边框 | `--border-subtle` / `border-jet-border` | 卡片边框、输入外围、容器分割 | 临时写灰色边框 |
| 轻分割线 | `--border-strong` / `border-jet-border-secondary` | 表格/卡片内部分隔、弱分割线 | 用 `--border-subtle` 堆出重边界 |
| 主操作/选中 | `--color-primary` / `text-jet-primary`、`bg-jet-primary` | 主按钮外的自定义主色、选中 icon、关键链接 | 自定义蓝色 hex |
| 主色反白文字 | `--color-primary-text` | 自定义主色块上的文字 | 假设永远是白色并写死 |
| 成功状态 | `--color-success`、`--color-success-soft`、`--color-success-border` | 在线、启用、成功、正常状态块 | 直接写绿色 hex/rgba |
| 警告状态 | `--color-warning`、`--color-warning-soft`、`--color-warning-border` | 待处理、风险、注意、部分异常 | 直接写黄色/橙色 hex/rgba |
| 错误状态 | `--color-error`、`--color-error-soft`、`--color-error-border` | 离线、失败、严重异常、删除风险 | 直接写红色 hex/rgba |
| 信息状态 | `--color-info`、`--color-info-soft`、`--color-info-border` | 信息提示、普通引导、非风险说明 | 滥用主色硬编码 |
| 字号 | `--fs-*` 语义字号优先 | 自定义标题、说明、指标、标签、代码外文本 | 直接写 `font-size: 14px` 或 `rem` |
| 间距 | `--space-*`、`--space-gutter` | padding、gap、margin、功能块间距 | 临时写 `10px`、`18px`、`30px` |
| 圆角 | `--radius-sm`、`--radius-base`、`--radius-lg`、`--radius-xl` | 标签、按钮组、卡片、弹层、概览容器 | 每个组件自己写 `border-radius` 数值 |
| 阴影 | `--shadow-subtle`、`--shadow-card`、`--shadow-pop`、`--shadow-lifted` | 卡片 hover、浮层、弹层、抽屉 | 临时复制 box-shadow |
| focus 态 | `--ring-focus` | 自定义可交互元素键盘焦点 | 只做 hover 不做 focus，或临时拼 shadow |
| sticky 边界 | `--shadow-sticky-top` | 底部 sticky 操作栏、吸底区域边界 | 用普通卡片阴影 |
| 代码/日志深色块 | `--code-dark-*` | 脚本、日志、配置片段、命令展示 | 在页面内新建一套深色主题 |

### 变量选择步骤

- 先按语义选变量，不按当前视觉颜色选变量：例如“离线”选 `--color-error-*`，不是找一个接近的红色。
- 先选组件默认能力，再选 Tailwind `jet-*` 原子类，最后才在 scoped CSS 中写 `var(...)` 组合。
- 同一个业务语义在同一页面只能选一组 token；例如所有“启用/正常”状态都用 `--color-success-*`，不要一处用绿色 hex、一处用 Ant Tag 默认色、一处用自定义 rgba。
- 没有合适 token 时，不要就地硬编码；先判断是否是公共语义，公共语义补到 `style.css`，一次性几何修正才允许写字面量。

### Tailwind 主题映射

`@theme inline` 暴露的 token 可用于 Tailwind 原子类，适合模板中直接表达简单样式；复杂组合或需要语义复用时仍写 CSS 变量。

- `text-jet-primary`、`bg-jet-primary-soft`、`border-jet-border` 等用于颜色、背景和边框。
- `text-jet-text`、`text-jet-text-secondary`、`text-jet-text-description`、`text-jet-text-disabled` 用于文本层级。
- `bg-jet-bg-layout`、`bg-jet-bg-container`、`bg-jet-bg-elevated` 用于页面、容器和浮层背景。
- `rounded-jet`、`rounded-jet-lg`、`rounded-jet-sm` 用于卡片、弹层、按钮组和小型标签。
- `shadow-jet`、`shadow-jet-secondary` 用于浮层、卡片和提升态。
- `text-jet-gray-*`、`bg-jet-gray-*`、`border-jet-gray-*` 只用于中性灰阶，不替代语义状态色。

## 字号使用

自定义文本字号优先使用 `style.css` 中的语义字号变量；Ant Design Vue 组件内的按钮、表单、表格、菜单、标签等字号按组件默认规范，不额外覆盖。

- 自定义字体统一使用 `--jet-theme-font-family` 或语义别名 `--font-sans`；Tailwind 场景使用 `--font-ali` 映射，不在业务组件中重新声明字体族。
- 可直接复用的基础字号变量包括 `--fs-10`、`--fs-12`、`--fs-14`、`--fs-15`、`--fs-16`、`--fs-17`、`--fs-18`、`--fs-19`、`--fs-20`、`--fs-22`、`--fs-24`、`--fs-26`、`--fs-28`，语义字号优先使用 `--fs-tiny`、`--fs-pill`、`--fs-meta`、`--fs-body`、`--fs-label`、`--fs-h4`、`--fs-h3`、`--fs-h2`、`--fs-h1`、`--fs-display`。
- `--fs-h1`：页面主标题、概览页核心标题，通常为 `24px`。
- `--fs-h2`：一级区块标题、详情页主区标题，通常为 `22px`。
- `--fs-h3`：卡片标题、分组标题、弹窗内主要标题，通常为 `18px`。
- `--fs-h4`：小区块标题、列表项标题，通常为 `16px`。
- `--fs-body`：正文、表单说明、普通列表内容，通常为 `14px`。
- `--fs-meta`、`--fs-label`、`--fs-pill`、`--fs-tiny`：辅助信息、标签、胶囊、角标，通常为 `12px`。
- 新增业务样式优先使用语义字号；`--fs-15`、`--fs-17`、`--fs-19` 只用于已有组件适配或明确的信息层级，不作为普通页面随手选值。不要在业务组件中随意新增 `13px`、`21px` 等孤立字号。
- 新增字体大小前，先检查 `style.css` 是否已有可复用 token；如果没有，优先在 `jetlinks-web-core/src/style.css` 中新增公共字号变量和语义别名，再在业务样式中引用。
- 字号必须使用 `style.css` 字号变量或 Ant Design Vue 组件默认字号，不在业务样式中用 `px` 或 `rem` 直接声明字号。

## 间距节奏

自定义布局间距使用 `--space-*` 变量表达，保持页面横向、纵向节奏统一；Ant Design Vue 组件内部 padding、gap、表单项间距、表格单元格间距不强行覆盖。

- `--space-1` 到 `--space-3`（`4px`、`8px`、`12px`）：图标与文字、标签内部、按钮组小间隔、紧凑列表项内部。
- `--space-4`（`16px`）：表单项组、卡片内部紧凑 padding、标题与内容的基础距离。
- `--space-5` 到 `--space-6`（`20px`、`24px`）：普通卡片 padding、筛选区与内容区距离、卡片之间的默认距离。
- `--space-7` 到 `--space-8`（`28px`、`32px`）：大区块之间、详情页分组之间、概览页模块之间。
- `--space-9` 到 `--space-12`（`36px` 到 `48px`）：首屏大模块、营销式头区、复杂工作台分区。
- `--space-section`（`64px`）：大段落或跨语义区块距离，普通后台表格页慎用。
- `--space-page`（`96px`）：页面级留白或特殊落地页节奏，常规业务页面不要默认使用。
- `--space-gutter`（`24px`）：栅格列间距、卡片网格间距和页面主内容 gutter。

## 标题与区块距离

页面标题、区块标题和副标题的间距必须稳定，不依赖临时硬编码。

- 页面主标题与副标题：主标题下方使用 `--space-1` 或 `--space-2`；副标题与首个内容区之间使用 `--space-5` 或 `--space-6`。
- 区块标题与副标题：标题和副标题之间使用 `--space-1`；副标题与正文/表格/卡片内容之间使用 `--space-4`。
- 只有标题没有副标题：标题与内容之间使用 `--space-4`；信息密度高的表格页可收敛到 `--space-3`。
- 卡片标题与卡片主体：优先使用 Ant Design Vue `a-card` 内建 header/body 间距；自定义卡片使用 `--space-4`。
- 分组标题与上一组内容：普通分组使用 `--space-6`；强语义大区块使用 `--space-7` 或 `--space-8`。

## 功能块内容节奏

功能块指页面中承担一个完整业务语义的局部区域，例如筛选区、统计区、详情区、表单分组、图表区、列表区、操作区、卡片内容区等。不要按具体 DOM 或组件类型限定间距，先判断内容之间的语义关系，再选择 `--space-*`。

- 同一标题组内部：标题、副标题、描述、状态标签、辅助说明之间使用 `--space-1` 到 `--space-2`。
- 标题组进入主体内容：标题、描述或状态信息到字段详情、表单、列表、图表、状态摘要之间使用 `--space-3` 到 `--space-4`。
- 主体内容内部重复项：字段行、指标项、标签项、列表摘要行、表单项组之间使用 `--space-2` 到 `--space-3`。
- 同一功能块内弱分组：基础信息与运行信息、配置项与说明、图表与图例等使用 `--space-4` 到 `--space-5`。
- 同一功能块内强语义分区：摘要区与明细区、筛选区与结果预览、图表区与记录列表等使用 `--space-5` 到 `--space-6`。
- 功能块与功能块之间：普通业务页使用 `--space-5` 到 `--space-6`；详情页或概览页中语义更强的模块分隔可使用 `--space-7` 到 `--space-8`。
- 若 Ant Design Vue 组件、项目封装组件或现有页面组件已提供稳定的 header/body、form item、table cell、card body 间距，优先保留组件默认节奏，不额外覆盖。
- 不要为了视觉对齐在局部样式中临时写 `10px`、`14px`、`18px`、`22px` 等孤立间距；需要调整时先映射到内容关系，再选择最接近的 `--space-*`。

## 卡片与容器距离

卡片优先使用 `a-card`、项目已有 Card 组件、`j-pro-table(card)` 或相邻页面既有容器；这些组件自身样式按组件规范处理，自定义卡片内容和组件外部间距再使用 `style.css` 变量。

- 页面根容器 padding：普通业务页使用 `--space-6`；嵌套详情或弹窗内部使用 `--space-4` 到 `--space-5`。
- 筛选区与结果区：使用 `--space-4` 到 `--space-6`，标准列表页默认 `--space-4`。
- 卡片与卡片之间：标准卡片网格使用 `--space-gutter`；纵向堆叠使用 `--space-4` 到 `--space-6`。
- 卡片内部 padding：普通卡片使用 `--space-5` 或 `--space-6`；紧凑信息卡使用 `--space-4`；小标签/统计小卡使用 `--space-3` 到 `--space-4`。
- 卡片标题区与操作区：标题、说明和右侧操作保持一行对齐，元素间距使用 `--space-2` 到 `--space-4`。
- 详情页左右栏或主从区域：栏间距使用 `--space-gutter`；不要用随意的 `18px`、`30px` 等非 token 值。

## 圆角与阴影

- `--radius-sm` / `--jet-theme-radius-sm`：小标签、小按钮、输入框附属元素和轻量胶囊。
- `--radius-base` / `--jet-theme-radius`：普通按钮、输入框、筛选容器、标准卡片。
- `--radius-lg` / `--jet-theme-radius-lg`：大卡片、弹窗、抽屉内容、概览区块。
- `--radius-xl`：需要比标准大卡片更柔和的局部容器；不要默认用于普通后台卡片。
- `--shadow-subtle`、`--shadow-card` / `--jet-theme-shadow-secondary`：普通卡片、轻量悬浮、可点击卡片 hover。
- `--shadow-pop`、`--shadow-lifted` / `--jet-theme-shadow`：弹窗、下拉浮层、抽屉、重要提升态。
- `--ring-focus`：自定义可交互元素的 focus 可见态；不要用临时 `box-shadow` 拼 focus ring。
- `--shadow-sticky-top`：底部操作栏或 sticky 区域边界，不用于普通卡片。

## 实现约束

- 能用 Ant Design Vue props、slots、size、status、type、variant、theme token 解决的，按 Ant Design Vue 方式实现，不写深层选择器覆盖。
- 自己写的内容能用 `style.css` token 或 Tailwind `jet-*` 原子类表达的，不在 scoped 样式里硬编码 hex、rgba、px、shadow。
- 自定义局部样式中确实无法用现有 token 表达的尺寸值，统一使用 `rem`，基准为 `16px`，例如 `14px` 写作 `0.875rem`、`16px` 写作 `1rem`、`24px` 写作 `1.5rem`；该规则适用于局部图形尺寸、定位修正等一次性几何值，但页面语义间距、字号、圆角、阴影、颜色仍必须优先使用 token。
- 业务状态块必须使用 `--color-success-*`、`--color-warning-*`、`--color-error-*`、`--color-info-*` 或 Ant Design Vue 状态能力，不允许直接写状态色 hex/rgba。
- 自定义可点击卡片、标签、Tab、工具栏按钮、列表行 hover、focus 态必须使用 `--surface-hover`、`--ring-focus`、`--shadow-*`、`--border-*` 等 token，不允许临时拼 hover/focus 样式。
- 局部样式只表达布局组合和业务状态，不复制公共主题变量已有能力。
- 新增公共 token 时命名必须体现语义，不要新增只服务单个页面的颜色或间距变量。
- 不要为了让 Ant Design Vue 组件匹配自定义 token 而大面积覆盖 `.ant-*` 内部结构；必须覆盖时限制作用域并说明兼容风险。
- 不要把卡片容器写成 `button`；可点击卡片使用语义容器加明确点击区域，或使用项目已有卡片组件。
- 不要在页面里混用多套灰阶、圆角、阴影和字号体系；同一页面必须能追溯到 Ant Design Vue 或 `style.css`。

## 自检清单

1. Ant Design Vue 组件是否保留组件自身规范，没有为了自定义 token 做不必要覆盖。
2. 自己写的内容是否已检查并使用 `jetlinks-web-core/src/style.css` 中存在的可复用 token。
3. 自定义标题、副标题、筛选区、内容区、卡片之间的距离是否使用 `--space-*`。
4. 自定义颜色、边框、背景、状态、字号、圆角、阴影是否来自 `style.css`。
5. scoped 样式是否只保留当前组件必要差异，没有复制公共工具能力。
6. 是否避免了深层覆盖 Ant Design Vue 内部选择器和硬编码设计值；若出现第二次相同字面量，是否已提升为 token 或改用已有 token。
7. 功能块之间、功能块标题组与主体内容、功能块内部子区域之间的距离是否按语义关系选择 `--space-*`，而不是按页面临时硬编码。
