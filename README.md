# JetLinks Develop Skills

JetLinks Enterprise 二次开发技能库。包含 AI 开发规则路由、Claude Code 配置、Cursor 规则和 JetLinks 脚手架开发规范。

## 目录结构

```
jetlinks-develop-skills/
├── jetlinks-secondary-development/
│   ├── SKILL.md                          # 主 Skill 入口 (Codex)
│   └── agents/openai.yaml                # Agent 配置
├── .claude/                              # Claude Code 配置
│   ├── config.json                       # 规则配置
│   ├── rules.md                          # 开发规则
│   ├── advanced-rules.md                 # 高级建议
│   └── README.md                         # Claude Code 使用说明
├── .prompt/                              # 核心规则文件
│   ├── ai-prompt.md                      # 总路由索引
│   ├── module-list.md                    # 模块发现指南
│   ├── module-reference.md               # 模块边界决策
│   ├── annotations-and-imports-reference.md # 注解与导入确认
│   ├── module-creation-rules.md          # 模块创建规则
│   ├── common-crud-rules.md              # 标准 CRUD 规则
│   ├── advanced-crud-rules.md            # 高级 CRUD 规则
│   ├── cross-service-call-rules.md       # 跨边界调用规则
│   ├── realtime-subscription-rules.md   # 实时订阅规则
│   ├── event-driven-rules.md             # 事件驱动规则
│   └── i18n.md                           # 国际化规则
├── .cursor/rules/
│   └── develop.mdc                       # Cursor 开发规则
└── ai-prompt.md                          # 总路由索引（根目录副本）
```

## 技能说明

### jetlinks-secondary-development

Codex Skill，用于分析和实现 JetLinks 脚手架任务。

**适用场景：**
- 创建或修改模块
- CRUD 代码生成
- 命令服务、事件驱动、实时订阅
- 国际化、导入确认、模块边界判断

**使用方式：**
1. 先阅读 `ai-prompt.md` 了解任务路由
2. 根据任务类型加载对应的 `.prompt/*.md` 规则
3. 以当前工作区真实代码为最终依据

## 关联项目

- [jetlinks-enterprise](https://github.com/jetlinks/jetlinks-enterprise) - JetLinks 企业版
