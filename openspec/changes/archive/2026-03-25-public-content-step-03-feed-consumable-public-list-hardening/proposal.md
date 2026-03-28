# 变更提案：Public Content Step 03 Feed 可消费公开列表加固

## 为什么要做

当前 `content` 已经有 `GET /content/posts/public` 的雏形，但它还不足以成为长期 feed 输入：游标语义需要加固，卡片字段需要稳定，且公开过滤与分页边界需要明确成可复用契约。

## 本次变更包含什么

- 加固公开帖子列表的游标、排序与过滤语义
- 稳定 feed 卡片最小字段集合
- 明确该列表只承接“可公开消费帖子输出”，不承担首页混排策略

## 本次变更不包含什么

- 首页默认 feed 聚合
- Agent 切换与混排策略
- 点赞、评论、收藏等互动摘要写入

## 预期结果

1. `content` 可以为后续 feed 模块提供稳定的可消费公开帖子列表。
2. 游标分页不会继续停留在含糊的时间戳近似语义上。
3. content 与 feed 的职责边界更清楚。

## 影响范围

- `apps/api/src/modules/content/*`
- `apps/api/src/modules/content/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`

