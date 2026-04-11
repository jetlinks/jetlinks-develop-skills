# JetLinks Develop Skills

JetLinks 团队自定义的 Codex skills 仓库。

仓库结构参考通用 skills 仓库约定，按 `skills/<skill-name>/` 组织，每个 skill 保持自包含，便于安装、分发和后续扩展。

## Repository Layout

```text
jetlinks-develop-skills/
├── README.md
└── skills/
    └── jetlinks-secondary-development/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── ai-prompt.md
            ├── module-list.md
            ├── module-reference.md
            └── ...
```

约定说明：

- 仓库根目录使用 `skills/` 作为技能集合入口，便于托管多个 skill。
- 每个 skill 目录只保留运行所需文件，例如 `SKILL.md`、`agents/`、`references/`、`scripts/`、`assets/`。
- 仓库级说明放在根 `README.md`，不要在 skill 目录里额外堆叠说明性文档。

## Available Skills

### `jetlinks-secondary-development`

用于 JetLinks 脚手架二开场景，帮助 Codex 在当前工作区内完成以下任务：

- 分析模块边界、目录落点和能力归属
- 按需加载 CRUD、事件、订阅、跨服务调用、i18n 等规则
- 基于当前仓库真实代码风格实现修改，而不是生成脱离上下文的模板代码

## Install

### Option 1: Use Codex skill installer

如果当前环境带有 `$skill-installer`，可直接按仓库路径安装：

```text
Use $skill-installer to install skill from https://github.com/jetlinks/jetlinks-develop-skills/tree/master/skills/jetlinks-secondary-development
```

也可以使用安装脚本：

```bash
python /path/to/install-skill-from-github.py \
  --repo jetlinks/jetlinks-develop-skills \
  --path skills/jetlinks-secondary-development
```

### Option 2: Manual install

将目标 skill 目录复制到本地 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/jetlinks-secondary-development "${CODEX_HOME:-$HOME/.codex}/skills/"
```

安装完成后重启 Codex，使新 skill 被重新发现。

## Usage

显式调用：

```text
Use $jetlinks-secondary-development to analyze this JetLinks scaffold task, find the correct module, load only the needed references, and implement the change.
```

典型请求示例：

- 使用 `$jetlinks-secondary-development` 为设备管理模块新增一个查询接口，并保持当前模块的响应式风格。
- 使用 `$jetlinks-secondary-development` 判断这个能力应该走直接依赖、命令服务还是事件机制，再实现代码。
- 使用 `$jetlinks-secondary-development` 在现有模块中增加订阅逻辑和对应的国际化文本。

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
4. 通过 PR 合入目标版本分支。

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
- 没有 PR 的直推提交流程，视为不符合规范
- 仓库默认模板见 `.github/pull_request_template.md`

## Skill Authoring Notes

为保证该仓库可持续扩展，新增 skill 时遵循这些规则：

- 新 skill 放在 `skills/<skill-name>/` 下。
- `SKILL.md` 只保留触发描述和执行流程，不放仓库级使用文档。
- 详细规则、索引和参考资料放入 `references/`。
- 需要 UI 元数据时，在 `agents/openai.yaml` 中维护。
- 新增或调整 skill 后，运行：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  skills/<skill-name>
```

## References

- OpenAI skills repository: https://github.com/openai/skills
- OpenAI curated skills layout: https://github.com/openai/skills/tree/main/skills
