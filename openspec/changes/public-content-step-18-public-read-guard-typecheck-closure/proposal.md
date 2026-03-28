# 变更提案：Public Content Step 18 公开读取守卫类型校验收口

## 为什么要做

最新 `public-content` 验收表明，公开首页 feed 与公开帖子详情这条“匿名可读 + 登录态增强”的主线虽然运行时行为已经正确，但配套新增的 `OptionalAuthGuard` 测试文件本身仍存在 branch-local 类型漂移。

当前 `apps/api/src/common/guards/__tests__/optional-auth.guard.spec.ts` 把自建的 ExecutionContext test double 整体断言成 `never`，导致 `ci:api:typecheck` 会直接失败。这意味着 public-content 系列虽然能通过 targeted Jest，却还不能把公开读取守卫的验收链真正收口。

本 step 继续沿用 `public-content` 作为 series prefix，只收口公开读取守卫测试与 public read 验收链的类型问题，不扩展新的 feed/detail 运行时语义或 auth 能力。

## 本次变更包含什么

- 对齐 `OptionalAuthGuard` 测试中的 ExecutionContext helper，让其与 Nest 最小类型边界兼容
- 保持公开首页 feed 与公开帖子详情“匿名可读 + 登录态增强”的既有运行时主线不变
- 重新执行公开读取相关 Jest / TSC 验收，并显式区分本 step 清理后的剩余基线问题

## 本次变更不包含什么

- 新的公开首页或公开帖子详情接口
- `OptionalAuthGuard` 的运行时语义重写
- 新的鉴权策略、权限模型或互动字段扩张

## 预期结果

1. `OptionalAuthGuard` 相关测试不再因为错误的 test double 类型断言打断 `ci:api:typecheck`。
2. 公开首页 feed 与公开帖子详情的可选认证读取主线可以继续通过代表性回归测试验证。
3. 后续再次验收 public-content 时，可以更清楚地区分 public-read 本地问题与仓库基线噪音。

## 影响范围

- `apps/api/src/common/guards/optional-auth.guard.ts`
- `apps/api/src/common/guards/__tests__/optional-auth.guard.spec.ts`
- `apps/api/src/modules/feed/*`
- `apps/api/src/modules/content/*`
