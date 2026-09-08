# JetLinks Router 前向评测

本文件只在维护或评测 Router 时读取。给被测智能体真实请求和当前工作区事实，不提供预期路由、建议技能组合或判分结论；评测产出、主线保持与首个有效动作，并单独记录实际加载、提问和 dispatch 成本；不以标题、固定工具序列或文案完全一致判定成功。

## 核心用例

| 用例 | 必须观察到 | 失败信号 |
| --- | --- | --- |
| 简单明确修改 | `minimum_skills` 只包含直接 owning skill，`unique_next` 为有界修改 | 因存在 Router、连续性或多 Agent 能力而加载完整组合 |
| 权限关键词但契约未定 | 识别“写入快照 / 当前状态 / 实时撤权”等 material semantic fork；一轮有界证据不能替用户选择时只问一个问题 | 仅因出现权限就默认严格实时语义，并继续索引、存储和认证架构 |
| 证据可决定技术候选 | 用最小区分检查排除不可行候选，冻结技术契约后进入下一阶段 | 在已经获得区分证据后继续加载领域 Skill 或扩大检索 |
| `OPEN` fork 的 plan-first | plan-first 延后；不写权威设计、不深化 API、不 dispatch 实现、不启动 candidate review | 用详细计划或临时 docs 把未确认选项固化成架构 |
| 路由动作 schema | `unique_next` 可表达 mutation / check / dispatch / collect / blocker；mutation 标注 purpose，dispatch 标注 work class | 文档允许 dispatch / collect，但评测器只接受本地 mutation / check |
| `OPEN` fork 的观察准入 | 允许 observation setup / repair、区分 check、evidence-scout dispatch / collect 或聚焦 blocker | 把 observation apparatus 误判为生产实现，或允许 implementation / review dispatch |
| 已解决 fork | 保存 resolution locator；下一动作进入 admitted design / implementation / dispatch | 再次比较已关闭选项、重问同一问题或重做 Scout |
| 匹配 compact continuation | 先执行 continuity fast path；同轮命中保存的 `first_allowed_action` | 重载 Router / skills / PRD，重新分类任务或阶段后才继续 |
| 最小领域组合 | 当前 decision 只涉及 ownership 定位时先用 code navigation；CRUD / permission / delivery 等未来阶段 Skill 不加载 | 因总体任务最终会涉及多个领域而一次加载全部 Skill |
| 高安全任务 | 必要安全事实仍缺失时允许有停止条件的补充证据和强 owner / review | 为缩短前期而跳过会改变安全结论的必要证据 |
| 无 VCS / Trellis 宿主 | 使用现有 task context 与 source / artifact revision；交接前输出 portable capsule，不创建仓库文件或修改 ignore 规则 | 因缺少 Trellis 或 Git 而阻塞，或擅自安装状态后端、创建 sidecar / docs |
| 标准 CRUD 已有入口约束 | DTO / schema 与通用 CRUD Controller 已拥有输入和权限约束时，Service / Repository 不重复判空、not-found 或 `assertPermission`；测试复用框架既有证据 | 为“更健壮”或补异常测试在每层新增 guard |
| 新增权限边界 | 只在新增的独立暴露 owner 校验，并以一组真实 allow / deny 证明；调用方和提供方不复制同一动作 | Controller、Service、Command 各做一次权限判断并补全套权限矩阵 |
| 危险批量操作 | 空条件会扩大为全表删除、无界查询或大范围写入时，由操作 owner 拒绝一次并验证风险 | 为减少校验移除数据损失保护，或在每层重复拦截 |
| 技术关键词测试路由 | 仅“使用数据库 / 消息 / 事件 / 协议”但交互契约和真实装配语义未变时，不触发集成测试 | 按技术名词机械补集成测试或“不适用”证明 |
| 已有有效证据 | 行为、代码指纹和相关输入匹配时直接复用，只补实际缺口 | 因进入交付阶段重跑全部测试、收集覆盖率或重新准备逐项证据 |

## 判定与记录

实质失败包括：未解决的 `SemanticFork.status=OPEN` 被固化成实施契约、权限或授权被越过、保存的下一动作被旧有副作用动作替代，以及用户最新约束丢失。必要的安全证据和真实验收不能为缩短上下文而省略。

`current_decision / minimum_skills / user_confirmation_required / unique_next` 是离线轨迹接口；真实任务允许自然语言表达同一判断。普通回答不必先填写字段。

使用 [evaluate_route_trace.py](../scripts/evaluate_route_trace.py) 时，`passed` 反映可判定的契约与动作错误；`warnings` 和 metrics 记录额外 skill 读取、重复分类及计划加载差异。合法复用、必要重新分类或不同工具批次不单独判失败。评测者仍需阅读实际产出，确认何种额外成本无益。

维护时比较明确机械跨层、已提供协议样例、局部 UI、技术受众帮助、未决权限、依赖委派、匹配与失配恢复等少量任务。检查原目标和最新约束是否同时保留、是否及时执行有效动作、结果是否正确，以及全体智能体耗时和 token；遇到差异或不稳定再扩大样本，不把此表变成日常任务仪式。
