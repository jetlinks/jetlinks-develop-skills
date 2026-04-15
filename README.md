# JetLinks Develop Skills

JetLinks 团队自定义的 Codex skills 仓库。

仓库结构参考 `awesome-claude-skills` 这类可直接扫描的仓库约定，skill 目录直接位于仓库根目录，每个 skill 保持自包含，便于安装、分发和自动识别。

## Repository Layout

```text
jetlinks-develop-skills/
├── README.md
├── .github/
│   └── pull_request_template.md
├── jetlinks-router/
├── jetlinks-protocol/
├── jetlinks-conventions/
├── jetlinks-reactive/
├── jetlinks-routing/
├── jetlinks-crud/
├── jetlinks-boundary/
├── jetlinks-events/
├── jetlinks-web/
├── jetlinks-capture/
└── jetlinks-delivery/
```

约定说明：

- 每个 skill 目录直接位于仓库根目录，方便被只做浅层扫描的工具自动发现。
- 每个 skill 目录只保留运行所需文件，例如 `SKILL.md`、`agents/`、`references/`、`scripts/`、`assets/`。
- 仓库级说明放在根 `README.md`，不要在 skill 目录里额外堆叠说明性文档。

## Available Skills

### `jetlinks-router`

总入口 skill，用于 JetLinks 二开场景下的任务分类与路由。

### `jetlinks-protocol`

用于协议包开发、协议阅读、传输编解码、二进制报文分析和联调排障。

### `jetlinks-conventions`

用于共享编码规范、注解/导入确认、命名约束，以及 i18n 判断与实现。

### `jetlinks-reactive`

用于响应式编程实践、非阻塞链路、批处理和 reactive 风险控制。

### `jetlinks-routing`

用于工作区结构发现、模块落点判断和新模块创建。

### `jetlinks-crud`

用于标准 CRUD、复杂查询、批量处理和 CRUD 相关副作用。

### `jetlinks-boundary`

用于直接依赖、命令服务、代理和跨模块边界选择。

### `jetlinks-events`

用于领域事件、生命周期事件、Topic 订阅和消息流处理。

### `jetlinks-web`

用于 JetLinks 前端页面开发、组件/hook/utils 能力复用、目录落点判断、状态管理与类型质量约束。

### `jetlinks-capture`

用于任务结束后的知识沉淀判断、经验归档、playbook 生成，以及决定是否需要继续更新 prompt 或 skill。

### `jetlinks-delivery`

用于提交信息、提交命令、分支策略、测试证据和 PR 描述整理。

## Scenario Routing

推荐按场景直接使用 focused skill，不确定时再走总入口：

- 不确定该用哪个 skill：`$jetlinks-router`
- 只想处理协议包、编解码、认证或二进制报文：`$jetlinks-protocol`
- 只想确认代码规范、导入、i18n 判断或国际化实现：`$jetlinks-conventions`
- 只想处理响应式链路：`$jetlinks-reactive`
- 只想找模块或新建模块：`$jetlinks-routing`
- 只想做 CRUD 或复杂查询：`$jetlinks-crud`
- 只想处理跨边界调用：`$jetlinks-boundary`
- 只想处理事件或订阅：`$jetlinks-events`
- 只想处理前端页面改造、能力复用或前端质量约束：`$jetlinks-web`
- 只想判断是否值得沉淀知识：`$jetlinks-capture`
- 只想整理提交、测试和 PR：`$jetlinks-delivery`

## Install

### Option 1: Use CC Switch (Recommended)

如果你用 CC Switch 管理 Claude Code、Codex、Cursor 等工具的 skills / prompts，推荐直接将本仓库作为 skill repository 接入：

1. 在 CC Switch 中添加仓库：`https://github.com/jetlinks/jetlinks-develop-skills`
2. 以仓库根目录作为扫描入口，不要额外指定 `skills/` 子目录
3. 同步或启用需要的 skill，例如 `jetlinks-router`、`jetlinks-crud`、`jetlinks-events`、`jetlinks-web`
4. 刷新或重启目标工具，使新 skill 被重新发现

校验方式：

```text
使用 $jetlinks-router 分类当前 JetLinks 二开任务，并选择最少必要的 focused skills 落地。
```

### Option 2: Use Codex skill installer

如果当前环境带有 `$skill-installer`，可直接按仓库路径安装：

```text
Use $skill-installer to install skill from https://github.com/jetlinks/jetlinks-develop-skills/tree/master/jetlinks-router
```

也可以安装 focused skill，例如：

```text
Use $skill-installer to install skill from https://github.com/jetlinks/jetlinks-develop-skills/tree/master/jetlinks-reactive
```

或：

```text
Use $skill-installer to install skill from https://github.com/jetlinks/jetlinks-develop-skills/tree/master/jetlinks-web
```

也可以使用安装脚本：

```bash
python /path/to/install-skill-from-github.py \
  --repo jetlinks/jetlinks-develop-skills \
  --path jetlinks-router
```

### Option 3: Manual install

将目标 skill 目录复制到本地 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R jetlinks-router "${CODEX_HOME:-$HOME/.codex}/skills/"
```

安装完成后重启 Codex，使新 skill 被重新发现。

## Usage

总入口调用：

```text
Use $jetlinks-router to classify this JetLinks scaffold task, choose the right focused skills, and implement the change.
```

Focused skill 示例：

- 使用 `$jetlinks-routing` 判断这个能力应该落在哪个模块。
- 使用 `$jetlinks-protocol` 分析协议包入口、编解码链路和二进制报文。
- 使用 `$jetlinks-crud` 为设备管理模块新增一个查询接口。
- 使用 `$jetlinks-reactive` 优化当前 `Mono` / `Flux` 链路并避免阻塞。
- 使用 `$jetlinks-boundary` 判断该能力应该走直接依赖还是命令服务。
- 使用 `$jetlinks-events` 为现有模块增加订阅逻辑。
- 使用 `$jetlinks-web` 在前端改造中优先复用 `@jetlinks-web-core/@jetlinks-web` 组件、hooks、utils，并按目录/状态/类型约束落地。
- 使用 `$jetlinks-delivery` 起草中文 commit、生成 shell 提交命令、整理测试证据和 PR 描述。

## Best Practices

完整实践见 [SECONDARY_DEVELOPMENT_PLAYBOOK.md](SECONDARY_DEVELOPMENT_PLAYBOOK.md)，涵盖：

- Claude Code / Codex / Cursor 的推荐协作方式
- 使用 CC Switch 安装本技能库的建议流程
- 简单 CRUD、复杂业务、测试修复等提示词模板与落地约束

## Git And PR Convention

JetLinks 项目交付代码时，默认遵循以下规范：

### Commit Title

- 提交标题优先对齐现有历史风格，采用 `type(scope): summary`。
- `type` 使用当前仓库已有语义，例如 `feat`、`fix`、`refactor`、`docs`、`test`。
- `scope` 使用受影响的业务域或模块名，例如 `基础模块`、`设备管理`、`prompt`。
- `summary` 使用简洁中文动宾短语，直接说明变更结果，避免空泛描述。

参考当前仓库已有风格：

- `refactor(prompt): 扩展低上下文边界决策规则`
- `refactor(基础模块): 优化菜单逻辑`
- `refactor(设备管理): 优化实体拓展型`

不建议：

- `update`
- `fix bug`
- `misc changes`
- 缺少 scope 的泛化标题，除非仓库历史本身就允许

### Branch Policy

- 禁止直接 push 到主干或集成分支，例如 `master`、`main`、`2.11`、`2.12`。
- 必须从目标基线分支拉出临时开发分支，再提交代码并发起 PR。
- 如果任务目标是发布到某个版本线，PR 的 base 必须明确指向对应版本分支。

推荐流程：

1. 从目标基线分支同步最新代码。
2. 创建临时分支实现需求或修复。
3. 完成测试后 push 临时分支。
4. 创建 PR 前先确认任务是否已完成：未完成用 draft，已完成再进入 review。
5. 通过 PR 合入目标版本分支。

### Testing Requirement

- 本次提交必须经过单元测试或集成测试，至少覆盖本次改动涉及的核心路径。
- 如果仓库已配置覆盖率阈值，提交前必须满足阈值。
- 如果仓库没有统一阈值，也必须在 PR 中给出可验证的覆盖证据，而不是只写“已测试”。
- 不能提供测试结果、覆盖率结果或失败原因的提交，不应进入待合并状态。

PR 中至少应提供这些数据：

- 执行过的测试命令
- 测试类型：单元测试、集成测试、端到端测试中的哪些
- 通过数量、失败数量、跳过数量
- 覆盖率数据，例如 line、branch、changed files 或 changed classes 的覆盖结果
- 若存在限制或未覆盖项，明确列出风险边界

### PR Description

PR 描述必须聚焦事实和结果，至少包含：

- 目的：为什么要做这次改动
- 核心变动：改了哪些模块、行为和边界
- 测试结果：命令、通过数、失败数、跳过数、覆盖率数据
- 风险与影响面：哪些场景受影响，哪些场景未覆盖

推荐模板：

```md
## 目的

- 修复 / 优化 / 新增什么能力
- 解决了什么问题

## 核心变动

- 模块 A：做了什么调整
- 模块 B：新增了什么约束或行为

## 测试结果

- 命令：`mvn -pl xxx -am test`
- 单元测试：42 passed, 0 failed, 1 skipped
- 集成测试：8 passed, 0 failed
- 覆盖率：line 81.4%, branch 73.2%

## 风险与说明

- 影响范围：
- 未覆盖场景：
- 回滚方式：
```

结论要求：

- 用数据说话，不要只写“测试通过”
- 没有覆盖率数据时，至少说明为什么缺失，以及提供了哪些替代证据
- 创建 PR 前先确认任务是否已完成：未完成使用 draft PR，已完成且用户确认后再 ready for review
- 默认不要在一个 PR 中提交大量代码，优先按清晰主题拆分
- 如果仓库远端是 GitHub，默认优先使用 `gh pr create` 创建 PR
- 在带沙箱的 agent 环境中，`gh` 命令应申请非沙箱执行
- 没有 PR 的直推提交流程，视为不符合规范
- 仓库默认模板见 `.github/pull_request_template.md`

## Skill Authoring Notes

为保证该仓库可持续扩展，新增 skill 时遵循这些规则：

- 新 skill 放在仓库根目录的 `<skill-name>/` 下。
- `SKILL.md` 只保留触发描述和执行流程，不放仓库级使用文档。
- 详细规则、索引和参考资料放入 `references/`。
- 需要 UI 元数据时，在 `agents/openai.yaml` 中维护。
- 新增或调整 skill 后，运行：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  <skill-name>
```

## References

- OpenAI skills repository: https://github.com/openai/skills
- OpenAI curated skills layout: https://github.com/openai/skills/tree/main/skills
