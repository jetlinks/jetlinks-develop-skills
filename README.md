# JetLinks Develop Skills

JetLinks 开发技能包。每个技能目录直接位于仓库根目录，包含 SKILL.md、agents/openai.yaml 及实际需要的 references / scripts / assets；运行时按当前任务选择加载。

## 职责与入口

已知负责当前动作的技能就直接使用；只有入口不明时才加载 router。开发约束在对应 owner 生效，review 不作为开工前置条件。

| 技能 | 负责 | 不替代 |
| --- | --- | --- |
| [jetlinks-router](jetlinks-router/SKILL.md) | 选择最少入口 | 领域执行与审批 |
| [jetlinks-routing](jetlinks-routing/SKILL.md) | 工作区、模块归属和创建 | 跨服务交互方式 |
| [jetlinks-boundary](jetlinks-boundary/SKILL.md) | 平台依赖、字段与对象关系建模、语义声明及命令 | 权限和消息交付 |
| [jetlinks-crud](jetlinks-crud/SKILL.md) | 查询、写入、状态动作、批量及校验 owner | 权限框架与执行机制 |
| [jetlinks-assets-permission](jetlinks-assets-permission/SKILL.md) | AssetsHolder 数据权限 | 普通业务关系建模 |
| [jetlinks-reactive](jetlinks-reactive/SKILL.md) | 订阅、事务连接、并发与背压 | 业务状态及投递承诺 |
| [jetlinks-events](jetlinks-events/SKILL.md) | 触发时机、消息投递与持续订阅语义 | 本地事务不变量 |
| [jetlinks-protocol](jetlinks-protocol/SKILL.md) | 注册、传输、报文与应答 | 产品专属业务 |
| [jetlinks-conventions](jetlinks-conventions/SKILL.md) | 职责、语义、通用性、运行状态和编码约定 | 各领域已拥有的细则 |
| [jetlinks-web](jetlinks-web/SKILL.md) | 页面任务、组件、交互及前端状态 | 后端契约与权限实现 |
| [jetlinks-review](jetlinks-review/SKILL.md) | 审查路径、证据、反例与判定 | 开发规则及自动修复授权 |
| [jetlinks-delivery](jetlinks-delivery/SKILL.md) | 提交信息、分支、推送与 PR | 再做设计或完整诊断 |
| [jetlinks-capture](jetlinks-capture/SKILL.md) | 稳定知识的归属与维护 | 任务流水和恢复状态 |
| [code-navigation](code-navigation/SKILL.md) | 定位与证据强度 | 架构决策 |
| [systematic-solving](systematic-solving/SKILL.md) | 竞争根因、未决契约和停滞诊断 | 已明确的正常实施 |
| [agent-orchestration](agent-orchestration/SKILL.md) | 已获允许的委派、验收与集成 | 自动获得委派权限 |
| [task-continuity](task-continuity/SKILL.md) | 长任务状态、恢复与交接 | 普通新任务的前置审计 |

## 使用原则

- 从当前动作出发，只读会改变本次决策的规则与章节；已核验的锚点和约束仍有效时复用。引用是条件导航，不是递归必读清单。
- 已接受的目标、约束和授权持续有效；只对无法从事实决定、会改变业务 / 安全 / 兼容契约的选择提问。
- 防止过度设计、重复校验、晦涩代码、魔法策略和特调：按 [职责与通用性](jetlinks-conventions/references/responsibility-and-generality-rules.md) 以及 [校验 owner](jetlinks-crud/references/common-crud-rules.md#校验范围与变化语义) 判断，不用关键词或数量阈值代替证据。
- 通用组件缺陷在所属组件修复并提交 PR，调用方接入正式修复；[修复闭环](jetlinks-conventions/references/root-cause-and-no-hack-rules.md#通用组件缺陷的闭环) 区分缺陷、能力缺口和业务差异。
- 在连贯阶段末集中验证，复用仍有效证据；不逐操作构建，不因进入提交阶段全量重跑。
- 用户可见输出只说明结果、必要决策、证据和真实风险，不展示所有内部检查、胶囊或“不适用”项目。

场景组合查 [路由补充](jetlinks-router/references/ai-prompt.md)，完整开发路径查 [二开指南](SECONDARY_DEVELOPMENT_PLAYBOOK.md)。两者均不要求普通任务预先读取。

## 安装

本包通过相对路径引用其他技能的规则，推荐完整安装根目录下所有含 `SKILL.md` 的技能，保持它们在同一 skills root 下的同级关系。完整安装只保证资源可用，执行时仍只加载当前任务需要的入口和细则。仅安装单个目录时，必须已有匹配版本的引用依赖；普通目录安装器不会自动解析这些依赖。

使用现有技能管理器时，将 `https://github.com/jetlinks/jetlinks-develop-skills` 作为技能仓库，扫描根目录，不添加 skills 子目录。有 skill-installer 的宿主可以执行以下请求：

```text
使用 $skill-installer，从 https://github.com/jetlinks/jetlinks-develop-skills 的 master 分支安装全部含 SKILL.md 的根级技能目录，保持各技能同级；不复制仓库 .codex 宿主配置。
```

手动安装沿用宿主已经发现的 skills root，完整复制上述技能目录；仓库根级维护脚本、文档和 `.codex/` 不属于技能安装内容。安装后可用下方 mirror 校验确认资源齐全且版本一致。不要在多个 root 放同名副本，也不自动修改用户配置。未发现变更时按宿主方式刷新。

## 可选宿主适配

通用检索、求解、协作和恢复不依赖 Git、Codex、Trellis 或固定后端。

- Codex 项目可使用已有 [.codex/config.toml](.codex/config.toml) 与四个 [叶子角色](.codex/agents/)，接入与运行验证见 [Codex 适配](agent-orchestration/references/codex-adapter.md)。仅安装技能不会启用多 Agent，也不覆盖宿主禁止委派的规则。
- 有结构化恢复需求时使用 [continuity 宿主适配](task-continuity/references/host-adapters.md)；未显式配置不安装 hooks、不建数据库。
- 已有 Trellis 的项目按 [集成规则](jetlinks-router/references/trellis-integration-rules.md) 接入，不双写恢复或权威状态。

## 验证

维护者在连贯修改阶段末运行：

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s scripts -p 'test_validate_skills.py'
```

比较已安装镜像时显式指定：

```bash
python3 scripts/validate_skills.py --mirror-root /path/to/installed/skills
```

结构校验覆盖 frontmatter、UI metadata、本地文件引用、公开资源、Python 接口及存在时的 Codex 适配；不证明智能体已正确理解。未改变脚本行为时，不为文案精简重复运行无关工具测试。

## 技能维护

- description 写能力和可辨识触发，正文保留关键不变量和直接动作；条件细则、案例、schema 和文献放 references，标明读取情境。
- 同一规则只有一个 owner；调用方引用，不复制另一套准入、审批、恢复或验证清单。保持技能名及公共工具接口稳定。
- 强约束写清触发、owner、禁止行为和合理反例。不要把某次失败、固定行数、目录数或字面量数量升级为通用硬门槛。
- 删除或合并文档前检查调用与独有规则；省上下文不能丢失安全、事务、授权及用户明确契约。
- 真实请求评估应区分结果、误触发 / 漏触发及成本。至少对照局部修改、独立安全边界、合理抽象、组件缺陷、并发事务与恢复场景；预期用例、结构测试和真实智能体行为评测分别报告。固定被测版本并核对实际加载的路径与内容，同名安装副本不能代表尚未同步的修订。

设计依据见 [约束与文献](jetlinks-conventions/references/design-constraint-sources.md)。技能格式参考 [Agent Skills](https://agentskills.io/specification)；文献与评测材料不加入业务任务默认读取链。
