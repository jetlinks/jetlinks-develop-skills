# JetLinks Web 交互方案目录（薄索引）

本文件已合并至 `jetlinks-web-style`，**唯一事实源**是：

- [`../../jetlinks-web-style/references/style-catalog.md`](../../jetlinks-web-style/references/style-catalog.md)

那里维护着完整的：

- 反传统后台感硬约束（编辑触发梯度、首屏不可叠加 + 一屏一主视觉锚点、状态先于字段 + 状态强调收口、信息密度目标、文案约束、弹窗不是唯一编辑路径、详情页 10 条硬规则 + AI 味 7 条不要 + 反向引用做主区段、侧栏 active 态分档 + 折叠 8 条精美规则、顶级路由不渲染 PageHead、浮动元素 z-index token 化）
- 业务任务 → 模版路由表
- 13 个交互模版（含 ASCII 线框骨架、核心组件、状态锚点、不借鉴清单、与相近模版的分界）：
  - 标准管理表格页
  - 资产卡片台账页
  - 筛选工作台页
  - 多对象对比页
  - 处置工作台
  - 对象详情工作区
  - 主从详情工作区
  - 配置态-运行态切换页
  - 配置向导 / 能力开通页
  - 资源 / 能力选择器
  - 监控感知页
  - 分析钻取页
  - 时间线 / 日志流页

## 使用约定

- 不要在本文件维护模版字段、骨架、组件清单或反例；任何更新都必须改 `jetlinks-web-style/references/style-catalog.md`。
- 在 `jetlinks-web` 主工作流中需要"先让用户选交互方案"时，加载 `../../jetlinks-web-style/SKILL.md`，并按 `style-catalog.md` 的"业务任务 → 模版路由"挑 2-4 个候选给用户。
- 不要把 `interaction-solution-catalog.md` 当作组件存在性的证据；组件仍以当前 workspace 的 `jetlinks-web-core` 为准。
- 用户已经命名了某个具体方案或"参考现在这个页面的结构"时，先在 `style-catalog.md` 中映射到最接近的模版，再继续。
