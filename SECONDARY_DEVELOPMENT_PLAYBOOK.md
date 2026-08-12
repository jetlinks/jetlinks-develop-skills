# JetLinks 二次开发最佳实践

本文面向 JetLinks 二开场景下使用 Claude Code、Codex、Cursor 等 AI 编码工具的团队协作。重点不是“换哪个模型”，而是让智能体先发现当前工作区事实，再调用合适的 JetLinks skill，最后给出可验证的实现和测试结果。

## 1. 先统一方法，再选工具

| 工具 | 推荐打法 | 更适合的任务 |
| --- | --- | --- |
| Claude Code / Codex | 一次性给出目标、边界、测试要求；复杂任务先让 agent 出计划并确认，再从扫描到实现、验证闭环执行 | 跨文件改动、批量修改、测试修复、交付整理 |
| Cursor | 建议分两轮：先找模块与相邻实现，再让它改代码和补测试 | 局部阅读、边写边审、人工介入较多的重构 |
| 共同要求 | 都要明确“先扫描再实现、复杂任务先计划后确认、不要凭空假设、只做最小必要改动” | 所有 JetLinks 二开任务 |

结论：

- Claude Code / Codex 更适合端到端执行。
- Cursor 更适合“先找参照，再局部落地”的编辑器内协作。
- 真正决定结果质量的不是工具名，而是有没有挂上 JetLinks skill 上下文，以及提示词里有没有写清边界、验收和测试要求。

## 2. 推荐安装本技能库

### 首选：CC Switch

推荐用 [CC Switch](https://github.com/farion1231/cc-switch/blob/main/docs/user-manual/zh/1-getting-started/1.2-installation.md) 管理本仓库，因为它更适合在多个 AI 工具之间复用同一套 skills / prompts。

建议流程：

1. 在 CC Switch 中添加 skill repository：`https://github.com/jetlinks/jetlinks-develop-skills`
2. 保持仓库根目录作为扫描入口，不要再手动指定 `skills/` 子目录
3. 同步或启用本仓库中的 JetLinks skills
4. 在目标工具中刷新 skills 配置或重启会话

验证是否生效，可直接发送：

```text
使用 $jetlinks-router 分类当前 JetLinks 二开任务，并选择最少必要的 focused skills 落地。
```

如果工具暂时不支持 `$skill-name` 这种显式写法，也可以直接写自然语言：

```text
请按 JetLinks 二开方式先扫描当前 workspace，再判断应该走模块定位、CRUD、跨边界调用、事件订阅还是交付测试流程，并只启用最少必要的规则。
```

### 备选：直接安装到 Codex

如果当前环境已经有 `$skill-installer`，或你只在 Codex 内使用本仓库，也可以按根 `README.md` 里的安装方式直接安装 focused skill。

## 3. 推荐的工作流

一个完整的 JetLinks 二开任务，建议按下面顺序推进：

1. 先路由
   - 不确定场景时，先用 `$jetlinks-router`
2. 复杂任务先计划
   - 新功能、跨模块、前后端联动、接口 / 数据结构 / 事件变更、需求仍在变化或会拆成多个子任务的任务，先输出计划并等待确认，并组合 `$jetlinks-systematic-solving` 建立可证伪的根因假设和验证矩阵。
   - 计划至少包含目标、范围、不做什么、实施步骤、风险 / 待确认点和验证方式。
   - 简单低风险小任务可在简短计划后直接实施。
3. 再发现
   - 扫描当前 workspace、父 `pom.xml`、相邻模块、现有 controller/service/entity/事件实现
4. 再落地
   - 只切到必要的 focused skill，例如 CRUD、boundary、events、reactive
   - 同一根因假设的一次实现仍未通过验收、故障转移到同类场景，或下一步需要继续增加条件 / fallback / retry / mock / 兼容分支时，停止编辑，回到 `$jetlinks-systematic-solving` 重建问题模型
5. 再验证
   - 在阶段边界集中跑相关测试；如果已有证据仍覆盖当前代码 / Git 指纹且相关输入未变化，直接复用，只补跑缺失或失效范围；如果当前工具不能直接执行，也要明确给出待执行命令和风险边界
6. 最后收尾
   - 需要提交、PR、测试证据时用 `$jetlinks-delivery`
   - 产出稳定经验时再用 `$jetlinks-capture`

交付阶段额外建议：

- 每个连贯阶段完成并集中验证后创建一个本地 commit，再用实际 commit hash 和下一步刷新任务运行态中的 Recovery Capsule
- 上下文压缩或恢复后先核对 task ID / revision、branch / HEAD、changed paths，再只读取胶囊列出的少量锚点；不要重新扫描全仓
- 创建 PR 前先确认任务是否已完成；未完成默认继续本地开发，只有用户明确要求中间共享时才开一个 draft
- 整个任务和总体验收完成后统一 push 并创建或更新一次 PR；PR 不记录每步进度
- 一个任务对应一个 PR；若需求含多个独立主题，先拆任务和验收标准，各任务完成后分别交付，不按执行阶段拆 PR

推荐的最小 skill 组合：

| 场景 | 推荐组合 |
| --- | --- |
| 不确定从哪下手 | `jetlinks-router` |
| 复杂、高难度或反复失败 | `jetlinks-systematic-solving` + 对应领域 skill |
| 简单 CRUD | `jetlinks-routing` + `jetlinks-crud` + `jetlinks-conventions` |
| 复杂业务 | `jetlinks-routing` + `jetlinks-boundary` + `jetlinks-events`，如链路是响应式再加 `jetlinks-reactive` |
| 测试、提交、PR 整理 | `jetlinks-delivery` |
| 任务结束后的经验沉淀 | `jetlinks-capture` |

## 4. 通用提示词骨架

无论你是在 Claude Code、Codex 还是 Cursor 中使用，建议都遵循同一个骨架：

```text
这是一个 JetLinks 二开任务。
请先扫描当前 workspace 和相邻实现，再选择最少必要的 JetLinks skills 落地。

目标：
- <要实现的业务目标>

约束：
- 如果任务复杂、跨模块、多子任务或需求仍在变化，先输出实施计划并等我确认，再修改代码
- 对复杂或高不确定性任务，先明确可观察目标、不变量、变化轴、竞争假设和能区分假设的证据；不要把计划本身当成问题分析
- 同一根因假设的一次实现仍未通过验收时，停止追加条件、fallback、retry、mock 或兼容分支；先说明新结果否定了什么，重建完整执行路径和验证矩阵后再继续
- 不要凭空假设模块名、包名、注解、Topic、命令 ID、表结构
- 保持与当前模块现有风格一致，只做最小必要改动
- 如果涉及跨模块能力，先判断应该用直接依赖、命令服务、事件还是订阅
- 如果涉及命令调用，优先复用当前模块已定义的 command 对象，并使用 `commandSupport.execute(...)`
- 如果涉及响应式链路，避免阻塞式写法
- 如果涉及用户可见异常，优先沿用当前模块的 `i18nCode` / message key 异常模型，不要在异常构造里写死 message

交付要求：
- 说明改动落在哪些模块 / 文件
- 运行相关测试，或明确给出测试命令、通过情况和未覆盖风险
- 已有阶段 / CI 证据仍有效时说明证据来源和对应指纹，不要仅因进入交付阶段重复执行
- 如果有稳定经验，收尾时再判断是否值得沉淀
```

这个骨架的关键价值是把 AI 约束在“先发现、证据驱动、停滞重构、可验证交付”四件事上，而不是让它直接开始生成代码或在同一假设上反复修补。

## 5. 提示词用例

### 简单 CRUD

适用：实体、Service、Controller 的标准新增或修改，包含常规增删改查、列表查询、详情和基础校验。

```text
使用 $jetlinks-routing、$jetlinks-crud 和 $jetlinks-conventions 处理这个 JetLinks 二开任务。

目标：
- 在当前工作区中为 <业务对象> 新增一个标准 CRUD 能力
- 包含列表、详情、新增、修改、删除

要求：
- 先扫描当前 workspace，找到应该落的模块和相邻 CRUD 示例
- 不要假设实体基类、控制器基类、注解导入和 i18n 约定
- 保持本地命名、返回结构、权限和校验风格一致
- 分析列表、详情、更新、删除、批量和导出是否需要 AssetsHolder 数据权限控制；资产类型、关联字段、权限动作、绑定关系或例外规则拿不准时先询问用户
- 保存前校验、唯一性冲突、资源不存在等用户可见异常，优先使用当前模块的 `i18nCode` / message key，而不是写死 message
- 只做和本次 CRUD 直接相关的最小改动
- 实现后运行相关测试，或给出可直接执行的测试命令与结果摘要
```

### 复杂业务

适用：需要跨模块能力、事件驱动、副作用同步、订阅处理、命令服务或响应式链路协作的场景。

```text
使用 $jetlinks-routing、$jetlinks-boundary、$jetlinks-events 处理这个 JetLinks 二开任务；如果目标模块是响应式链路，再补充 $jetlinks-reactive。

场景：
- <描述业务目标，例如：设备规则发布后，需要通知其他模块、写入审计记录，并向订阅方推送结果>

要求：
- 如果这是较大的后端改动或新功能，先把待确认设计和测试目标写入 Trellis active task 的归属 artifact，把实时任务拆分写入非版本化 runtime / checkpoint；无此载体或无 Trellis 时写入经 Git 忽略验证的单一运行态文件。确认后只把长期稳定结论原位提升到权威 docs
- 先扫描现有模块边界、命令服务、事件监听器、订阅处理器和相邻实现
- 不要默认新增直接依赖，先判断该走直接依赖、命令服务、事件还是订阅
- 如果已有 `QueryCommand` 或本地 command DTO，优先使用 `commandSupport.execute(...)`，不要直接退化成 `executeToMono(...)`
- 如果链路已有 Mono / Flux 风格，保持非阻塞实现
- 对响应式链路里的用户可见异常，优先传递带 `i18nCode` / message key 的异常，不要直接 `Mono.error(new XxxException(\"...\"))`
- 拆清主流程和副作用流程，不要把复杂副作用硬塞进 controller
- 输出最终的边界选择理由、核心改动点和验证方式
```

### 测试与修复

适用：补测试、修失败测试、交付前补验证证据，或要求 agent 明确给出测试命令和风险边界。

```text
使用 $jetlinks-delivery 处理这个 JetLinks 测试任务；如果已经知道改动属于哪个业务域，再结合对应 focused skill 一起执行。

目标：
- 为 <改动点 / 模块> 补充测试，或修复相关失败测试

要求：
- 先扫描当前模块已有测试风格和相邻测试类
- 优先覆盖这次改动涉及的核心路径、边界条件和异常分支
- 测试目标必须映射真实使用场景和真实数据形态，不允许为了让测试通过而删除测试、弱化断言、只 mock 被测核心逻辑或只跑无关测试
- 运行相关测试命令，并给出 passed / failed / skipped 结果
- 先映射已有证据到验收矩阵；记录对应 commit / tree / diff 指纹，相关代码、测试、配置、依赖、base 和环境未发生影响结果的变化时直接复用
- 如果仓库已有覆盖率要求，补充覆盖率数据；如果没有，也要说明替代验证证据
- 明确列出仍未覆盖的风险边界，不能只写“已测试”
```

## 6. 实践约束

- 不要只说“帮我做个功能”，至少要给业务目标、约束和验收结果。
- 不要让 AI 凭记忆猜模块名、注解、包结构、Topic 或命令 ID。
- 简单 CRUD 不要上升成复杂架构；复杂业务也不要只靠一个 CRUD 提示词硬顶。
- 较大的后端改动或新功能必须先设计、落档、确认，再按测试目标开发。
- CRUD 相关能力必须显式判断是否需要走 `AssetsHolder` 数据权限，不确定就问，不要手写平行的租户 / 部门 / 创建人过滤。
- 已有命令对象时，优先要求 AI 使用显式 command + `commandSupport.execute(...)`，不要默认改成 `executeToMono(...)` 这类快捷写法。
- 对用户可见异常，默认要求走 `i18nCode` / message key + 参数模式；只有目标模块的旧异常模型只支持 `message` 时，才回退到本地化后的文本。
- 如果使用 Cursor，优先两轮式提示：第一轮找模块与相邻实现，第二轮再修改代码。
- 如果使用 Claude Code 或 Codex，可以把“扫描、实现、测试、交付”作为同一任务结果，但实时过程留在 task runtime，不生成仓库阶段总结。
- 测试要求必须写清楚，至少要落到“执行什么命令、结果如何、还有什么没覆盖”。
- 交付不等于重新测试：已有证据覆盖验收矩阵且代码 / Git 指纹和相关输入仍有效时复用，只补跑缺失、失效或有时效性的检查。
- 发 PR 前先明确“这次任务是否已完成”；未完成默认不 push / 不开 PR，避免把 draft / PR 评论当进度流水。
- 不建议把大范围重构、功能开发、测试修复和文档整理一起塞进一个 PR。
- 改动完成后，如果结论已经稳定、可复用，再考虑用 `$jetlinks-capture` 沉淀为 playbook、knowledge 或 skill 更新。

## 7. 一个可直接复用的起手式

如果你不想每次都重新组织语言，可以直接从下面这段开始：

```text
这是一个 JetLinks 二开任务。请先扫描当前 workspace 和相邻实现，再选择最少必要的 JetLinks skills 落地，不要凭空假设模块名、包名、注解、命令 ID 或 Topic。较大的后端改动或新功能先把待确认设计和测试目标写入 Trellis active task 的归属 artifact，把实时计划和 Recovery Capsule 写入非版本化 runtime / checkpoint；没有这种载体或没有 Trellis 时，使用经 Git 忽略验证的单一运行态文件，等我确认后再开发。仓库 docs 只原位维护当前已接受的长期设计，不追加进度、失败或阶段总结。上下文恢复后先核对 task 和 Git 指纹，只读取胶囊锚点后继续，不重新全仓扫描。每个连贯阶段完成并验证后先创建一个本地 commit，再用实际 hash 刷新胶囊；整个任务验收完成后才统一 push 并创建或更新一次 PR，禁止逐步骤推送或用 PR 记流水。涉及 CRUD 时分析是否需要 AssetsHolder 数据权限控制，不确定就问。保持当前模块风格一致，只做最小完整改动。实现完成后，请给出改动点、测试结果和风险边界；只有产出了跨任务稳定经验时再判断是否更新已有知识或 skill。
```

再在后面补上你的具体业务目标即可。
