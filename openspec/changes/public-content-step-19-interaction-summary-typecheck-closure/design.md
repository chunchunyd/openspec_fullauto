## Context

step-11 已经把互动摘要投影主线落到了正式服务层，最新 public-content 验收也确认 `interaction-summary.service.spec.ts` 在运行时是绿的。

但这组测试当前依赖 `jest.Mocked<PrismaService>` 去承接深层 Prisma delegate，而 `groupBy` 在类型上仍然保留 Prisma 原始方法签名，不是 `jest.Mock`。于是运行时可以调用 `.mockResolvedValue(...)`，TypeScript 却会在多个点位直接报错。

这说明互动摘要的运行时行为、测试夹具和最小类型校验链之间还没有真正闭环。

## Goals / Non-Goals

**Goals:**

- 让 `InteractionSummaryService` 测试使用显式、类型兼容的 Prisma / repository mock 结构
- 保持详情、批量摘要和 feed 卡片摘要的当前投影语义不变
- 让 public-content rerun 验收可以把 interaction-summary 本地问题与仓库基线问题分开识别

**Non-Goals:**

- 不新增新的互动计数或聚合口径
- 不重写 `InteractionSummaryService` 的运行时投影逻辑
- 不承接整个 monorepo 的 Prisma mock 通用化重构

## Decisions

### 1. 用显式 mock 句柄承接 Prisma delegate，而不是依赖深层 `jest.Mocked<PrismaService>` 推导

本 step 会为 `postLike.groupBy`、`postFavorite.groupBy` 和 `comment.groupBy` 建立显式 mock 句柄，或定义一个只覆盖测试所需字段的最小 `MockPrismaService` 结构。

不继续依赖深层 delegate 自动推导，因为这会让运行时测试通过、类型检查失败的漂移持续隐藏在验收链里。

### 2. 把 interaction summary 测试看作摘要投影契约的一部分

本 step 不把 `interaction-summary.service.spec.ts` 当成可随意漂移的临时 mock 文件，而是把它视为详情、批量摘要与 feed 卡片摘要投影契约的一部分。

因此测试夹具需要和当前摘要语义一起保持稳定，而不是靠 `as any` 或类型漂移侥幸通过。

### 3. 验收必须同时覆盖运行态与类型态

本 step 的验收至少会覆盖：

- `interaction-summary.service.spec.ts`
- interactions 代表性测试
- `apps/api` TypeScript 检查

并在结果中显式区分：

- 本 step 已清掉的 interaction-summary 本地问题
- 仓库其他模块现存的基线问题

## Risks / Trade-offs

- [TSC 仍可能暴露其他非 interaction-summary 的本地或基线问题] -> 本 step 至少清掉 summary 测试自身引入的问题，并把剩余问题显式隔离
- [显式 mock 结构会让测试更啰嗦] -> 这是可接受代价，优先保证契约和验收链真实可依赖
- [调整测试夹具后可能暴露更多摘要断言漂移] -> 这是目标的一部分，应尽早暴露

## Migration Plan

本 step 不涉及数据库迁移。实施顺序是先收口 summary 测试夹具的类型表达，再 rerun interactions 相关 Jest 与 TypeScript 验收。

## Open Questions

- 当前没有额外开放问题；若实现时发现可以提取复用的 `groupBy` mock helper，也应限制在 interactions 测试范围内，不扩成全仓库测试基础设施重构。
