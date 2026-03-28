# 变更提案：Public Content Step 19 互动摘要类型校验收口

## 为什么要做

最新 `public-content` 验收表明，`InteractionSummaryService` 的运行态测试虽然已经通过，但新增的 `interaction-summary.service.spec.ts` 仍把 Prisma delegate 的 `groupBy` 方法直接当成 Jest mock 使用。

这会让 `postLike.groupBy`、`postFavorite.groupBy` 和 `comment.groupBy` 在 TypeScript 里继续保留 Prisma 原始方法签名，进而在 `.mockResolvedValue(...)` 处触发多处 `TS2339`。结果是 public-content 的互动摘要主线在 Jest 看起来是绿的，但 `ci:api:typecheck` 依旧无法真正收口。

本 step 继续沿用 `public-content` 作为 series prefix，只收口互动摘要测试夹具与类型校验链，不扩展新的互动语义、计数规则或摘要字段范围。

## 本次变更包含什么

- 对齐 `interaction-summary.service.spec.ts` 中 Prisma / repository test double 的类型表达
- 保持帖子详情、批量摘要和 feed 卡片摘要的既有运行时语义不变
- 重新执行 interactions 相关 Jest / TSC 验收，并显式区分本 step 清理后的剩余基线问题

## 本次变更不包含什么

- 新的互动摘要字段、统计口径或聚合策略
- 新的点赞、收藏、评论或关注行为语义
- `InteractionSummaryService` 之外的全仓库 Prisma mock 重构

## 预期结果

1. `interaction-summary.service.spec.ts` 不再因为 Prisma delegate mock 类型不兼容而打断 `ci:api:typecheck`。
2. 帖子详情、批量摘要和 feed 卡片摘要的最小互动投影继续有可依赖的回归测试覆盖。
3. 后续再次验收 public-content 时，可以更清楚地区分 interaction-summary 本地问题与仓库基线噪音。

## 影响范围

- `apps/api/src/modules/interactions/interaction-summary.service.ts`
- `apps/api/src/modules/interactions/__tests__/interaction-summary.service.spec.ts`
- 必要时的 `apps/api/src/modules/interactions/dto/*`
