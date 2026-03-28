# 变更提案：Public Content Step 12 Feed 与 Detail 契约回对齐

## 为什么要做

`series/public-content` 本轮验收表明，首页 feed 与公开帖子详情这两条读侧主线虽然已经具备基础输出，但真实契约仍有三处关键漂移：

- 已登录调用方经过 public feed / public detail 读取时，拿不到当前用户自己的 `isLiked` / `isFavorited` 状态
- `limit` 查询参数在 content / feed 读侧上没有稳定完成数字转换，真实 HTTP 请求会出现文档可用但接口 400 的情况
- public post detail 的 `updatedAt` 被错误回填为 `createdAt`

这个 step 继续沿用 `public-content` 作为 series prefix，只收口 public feed 与 public detail 的读取契约，让它们重新和 step-02、step-04、step-06、step-11 已承诺的行为保持一致。

## 本次变更包含什么

- 为 public feed 与 public post detail 建立“可匿名读取、带合法 token 时补当前用户互动状态”的受控可选鉴权读取路径
- 对齐 content / feed `limit` 查询参数的解析与校验，让公开读侧分页输入与文档一致
- 修正 public post detail 的 `updatedAt` 映射与等价契约表达，并补齐对应回归保护

## 本次变更不包含什么

- 公开互动对象的可见性边界修复
- comments list 的父帖子 404 契约修复
- interactions service 测试基建恢复或行为信号写入扩展

## 预期结果

1. public feed 与 public post detail 继续允许匿名读取，但已登录调用方能够拿到和自己一致的最小互动状态。
2. content / feed 的 `limit` 查询参数可按文档稳定工作，public post detail 的 `updatedAt` 语义真实可信。
3. 读侧 DTO、Swagger / OpenAPI 与真实返回保持一致，不再需要客户端靠猜测补逻辑。

## 影响范围

- `apps/api/src/common/guards/*`
- `apps/api/src/modules/content/*`
- `apps/api/src/modules/feed/*`
- `apps/api/src/modules/interactions/interaction-summary.service.ts`
- `packages/api_contracts/openapi/openapi.json`
