# 变更提案：Public Content Step 15 评论分页查询契约对齐

## 为什么要做

最新验收表明，`GET /interactions/comments/post/:postId` 虽然在文档里声明支持 `limit` 分页参数，但真实 HTTP 请求把 `limit=20` 作为查询字符串传入时，仍可能因为 DTO 没有完成显式数字转换而被 `@IsInt()` 判成 400。

这意味着 comments list 当前还没有真正兑现 step-13 已归档的“文档允许范围内的评论 `limit` 应被稳定解释”的承诺。

本 step 继续沿用 `public-content` 作为 series prefix，只收口 comments list 的 HTTP 查询分页契约，不扩展新的评论能力或共享契约导出主题。

## 本次变更包含什么

- 对齐 comments list `limit` 查询参数的显式数字转换与范围校验
- 让 controller / DTO 行为与现有接口文档保持一致
- 为代表性分页输入补齐回归测试

## 本次变更不包含什么

- 评论父帖子公开性边界返工
- 新的评论交互能力
- 共享 OpenAPI 产物导出收口

## 预期结果

1. `GET /interactions/comments/post/:postId` 可以稳定接受文档允许范围内的 `limit` 查询参数。
2. 只有真正越界或非法的分页值才会被拒绝。
3. comments list 的真实 HTTP 行为与当前 OpenSpec / Swagger 描述重新一致。

## 影响范围

- `apps/api/src/modules/interactions/comments.controller.ts`
- `apps/api/src/modules/interactions/dto/comments.dto.ts`
- `apps/api/src/modules/interactions/__tests__/*`
