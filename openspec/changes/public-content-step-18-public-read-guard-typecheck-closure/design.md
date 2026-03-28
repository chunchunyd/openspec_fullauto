## Context

step-12 与 step-13 已经把公开首页 feed、公开帖子详情和可选登录态增强主线落到了正式控制器与守卫链里，最新验收也确认运行态 targeted Jest 是通过的。

但新增的 `OptionalAuthGuard` 测试把自建 context 整体断言成 `never`，导致 `switchToHttp()` 等最小接口在 TypeScript 里直接丢失。结果就是：

- Jest 运行时看起来正常
- `pnpm --dir apps/api exec tsc -p tsconfig.json --noEmit` 却会被 public-content 自己新增的测试文件打断

这说明公开读取守卫的运行时行为、测试夹具和验收链之间还没有形成稳定闭环。

## Goals / Non-Goals

**Goals:**

- 让 `OptionalAuthGuard` 测试使用与 Nest 最小 `ExecutionContext` 形状兼容的 test double
- 保持公开首页与公开帖子详情现有的“匿名可读 + 登录态增强”语义不变
- 让 public-content rerun 验收可以把本地 public-read 问题与仓库基线问题分开识别

**Non-Goals:**

- 不重写 `OptionalAuthGuard` 的运行时语义
- 不新增新的公开读取接口、字段或权限分支
- 不承接整个 `apps/api` 的历史类型债务清理

## Decisions

### 1. 用最小兼容的 ExecutionContext test double 替代整体 `never` 断言

本 step 会把 `OptionalAuthGuard` 测试里的 context helper 调整成最小但类型兼容的 test double，或仅在调用点做窄范围断言，而不是把整个对象整体断言为 `never`。

不继续依赖 “运行时能过就行” 的写法，因为这会让最小类型校验链失去发现 public-content 本地回归的能力。

### 2. 把 OptionalAuthGuard 测试视为 feed/detail 公开读取边界的一部分

虽然报错点位于 `common/guards`，但该测试实际承接的是公开首页与公开帖子详情这条共享的可选认证读取主线。

因此本 step 不把它当成孤立的 auth 单测修补，而是当成 public-content 公开读取验收链的一部分来收口。

### 3. 验收必须同时覆盖 guard 单测、public read 代表性主线与 TypeScript 检查

本 step 的验收至少会覆盖：

- `OptionalAuthGuard` 相关 Jest
- `feed` / `content` 代表性读取测试
- `apps/api` TypeScript 检查

并在结果中显式区分：

- 本 step 已清掉的 public-content 本地问题
- 仓库其他模块现存的基线问题

## Risks / Trade-offs

- [TSC 仍可能暴露其他非 public-content 基线债务] -> 本 step 至少清掉 guard test 自身引入的问题，并把剩余噪音显式隔离
- [测试 helper 类型收紧后可能暴露更多断言漂移] -> 这是目标的一部分，优先让验收链真实反映当前边界
- [误把测试改动扩成 auth 运行时重构] -> 通过 tasks 明确限制在 guard test double 与公开读取验收链范围内

## Migration Plan

本 step 不涉及数据库迁移。实施顺序是先收口 guard test double 的类型表达，再 rerun 公开读取相关 Jest 与 TypeScript 验收。

## Open Questions

- 当前没有额外开放问题；若实现时发现 `OptionalAuthGuard` 需要补充更明确的最小 helper 类型，应限制在测试夹具范围内，不扩成通用 auth 基础设施重构。
