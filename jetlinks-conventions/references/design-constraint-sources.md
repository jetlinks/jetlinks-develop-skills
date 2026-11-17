# 简洁设计约束的依据与适用边界

用于维护开发 / 审查规则，非普通任务必读材料。2026-11-16 核对以下官方工程指南及原作者资料；它们支持设计判断，不证明某段提示词已经能约束智能体行为。

业务任务出现依据缺口时，可定点查相关规范；何时扩展及何时停止由 [扩大依据规则](../../systematic-solving/references/systematic-solving-rules.md#扩大依据的时机) 拥有，不要求先读完本文或整套研究资料。

## 文献到约束

| 依据 | 本技能采用的判断 | 不能推导成 |
| --- | --- | --- |
| [Google：What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html) | 过度设计是超出当前需要的泛化 / 能力；复杂度看读者理解与修改出错成本；名字表达意图，注释解释原因 | 所有接口、长文件、链式调用或额外方法都有问题 |
| [Fowler：YAGNI](https://martinfowler.com/bliki/Yagni.html) | 不提前实现假想未来功能；改善可修改性的重构、测试与交付能力不因 YAGNI 被禁止 | 单一消费者不能抽象、缺陷只补当前场景，或可以忽略长期代码健康 |
| [Fowler：Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html) | 正确性与表达意图优先，再消除重复和不必要元素 | 为减少类 / 方法数把多个阶段压成一条长链，或把视觉相似强行合并 |
| [OWASP：Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) | 不可信输入做语法和业务语义校验，优先框架 / schema；输入有效不等于已获授权 | “内部调用可信”即可跳过独立入口，或只判类型便省略范围、状态和安全约束 |
| [Fowler：Replace Magic Literal](https://refactoring.com/catalog/replaceMagicLiteral.html) | 有业务 / 策略含义的字面量用可理解符号表达，并保留单位与依据 | 每个 0 / 1 都要常量化，或把任意数字改名就能证明策略合理 |

Google 的测试建议是其工程语境；本包按变化选择有效证据，不照搬为每次改动必须新增单元测试。OWASP 规定不可信边界的必要校验，并未主张减少安全检查；“同链重复校验在唯一 owner 收敛”是结合 JetLinks 契约的工程规则，不能冒充 OWASP 原文。

通用组件缺陷回到 owner 修复并提交 PR、应用禁止依赖平台 manager、2.21 字段扩展及 AssetsHolder 统一契约，属于本项目要求，不包装成通用行业定律。

## 如何写给智能体

一条强约束应能说明：

- **触发与 owner**：何时适用，哪一层已有保证，当前代码路径在哪里。
- **行为与原因**：应保留 / 修改什么，实际改变哪项契约或维护成本。
- **合理反例**：什么看似相同却不适用，避免按关键词删代码。
- **证据**：什么观察能证实判断，怎样在阶段末验证改变的行为。

这些要素用于写规则，不要求智能体对每个 guard、常量或方法填写审计表。

## 重点约束归属

- 过度设计、可读性、魔法值、场景特调：[职责与通用性](responsibility-and-generality-rules.md)。
- 重复校验与真实信任 / 状态边界：[CRUD 校验](../../jetlinks-crud/references/common-crud-rules.md#校验范围与变化语义)。
- 通用组件缺陷与正式修复：[根因处理](root-cause-and-no-hack-rules.md)。
- 判断强度、合理反例与报告：[审查方法](../../jetlinks-review/references/review-method.md)。

使用 [正反场景](../../jetlinks-review/references/evaluation-cases.md) 检查误触发与漏检；只有实际执行了被测智能体任务才能报告行为评测结果。结构验证、人工规则走查与预期用例不能代替该结果。
