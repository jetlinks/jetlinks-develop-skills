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
