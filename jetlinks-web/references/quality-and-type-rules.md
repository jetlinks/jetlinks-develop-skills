# JetLinks Web Quality And Type Rules

本文件整合交付质量约束与 TypeScript 约束，作为前端改动的统一兜底规则。

## 适用范围

- 页面或模块改造后的交付前自检
- 需要控制 `any` 扩散和断言风险的改动
- Code Review 前的质量与类型一致性检查

## 必须遵守

- 优先复用 `@jetlinks-web-core` 与 `@jetlinks-web` 的现有能力。
- API 请求统一落 `api/*.ts`，避免页面内硬编码接口。
- 复杂逻辑优先抽离到 hook 或 service。
- 新增能力前先确认是否已有同类实现可复用。
- 关键边界补齐类型：API 入参/出参、组件 props、store state、路由参数。

## Web Code Generation Constraints

以下约束用于补充页面生成、组件拆分与交付质量规则：

1. JSX/Vue 文件超过 300 行时必须拆分为子组件，避免单文件持续膨胀。
2. 出现 2 处及以上重复结构时，必须优先提炼复用组件，而不是继续复制实现。
3. API 请求不能直接写在组件内，统一下沉到 `api/*.ts` 或 service 层。
4. 业务逻辑必须抽离到 hook 或 service，组件只负责 UI 组合与事件分发。
5. UI 组件必须保持无副作用，避免在渲染组件中散落请求、全局状态写入或环境依赖。
6. 组件架构层级不得超过 5 层，避免形成过深的包装链与调试负担。
7. 当 props 超过 3 个时，必须评估是否需要做接口抽象、上下文收敛或组件职责拆分。
8. 必须使用 TypeScript，为 props、接口数据、状态与关键函数入参/返回值补齐类型。
9. 页面或关键区域必须提供 loading、error、empty 状态，避免无反馈或空白界面。
10. 优先复用现有组件，再考虑新增组件，避免在业务侧重复封装已有能力。
11. 必须使用统一组件库（如 Ant Design 或现有 Design System），避免混用零散 UI 风格。

## 高频事件请求控制

- 对同一事件或同一触发源的高频请求（如输入搜索、滚动加载、窗口 resize、频繁点击）必须评估并使用防抖或节流。
- 输入类、筛选类、联想搜索类请求优先用防抖；滚动监听、拖拽、持续触发类请求优先用节流。
- 禁止在高频事件中直接发起无控制请求，避免重复调用、接口抖动与页面卡顿。
- 若业务必须实时请求，需说明原因并补充并发控制策略（如取消前序请求、忽略过期响应）。

## Vue Props 语法限制

- 在 `Vue 3` 的 `script setup lang="ts"` 组件中，`props` 统一使用运行时对象语法声明，不使用泛型写法 `defineProps<T>()`。
- 需要类型约束时，使用 `PropType` 绑定具体字段类型，并在 `required`、`default` 等运行时配置中显式声明。
- 错误写法：`defineProps<GaugeWidgetProps>`
- 正确写法示例：

```ts
const props = defineProps({
  info: {
    type: Object as PropType<GaugeInfo>,
    required: true
  },
  style: {
    type: [Object, String] as PropType<GaugeWidgetProps['style']>,
    default: () => ({})
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})
```

## 禁止模式

- 提交调试日志、注释掉的废弃代码、临时代码块。
- 在组件中硬编码后端路径、权限规则或环境配置。
- 使用 `as any` 或大范围 `any` 直接绕过类型错误。
- 同一业务模型在多处重复且冲突定义。
- 使用泛型 `defineProps<T>()` 声明组件 props。

## 交付前检查建议

1. 执行目标项目构建或类型检查命令（如 `pnpm build`、`pnpm typecheck`）。
2. 对关键链路做冒烟验证：查询、保存、删除、路由跳转、权限按钮。
3. 若改动影响通用能力，补充最小可复现验证路径。
4. 说明未执行的检查项及原因（如环境限制、依赖缺失）。

## 自检清单

- 是否避免了重复实现并复用了既有能力。
- 是否补齐了关键入参、出参与状态类型。
- 是否收敛了 `any` 的范围并避免无边界断言。
- 是否验证了关键交互与权限行为。
