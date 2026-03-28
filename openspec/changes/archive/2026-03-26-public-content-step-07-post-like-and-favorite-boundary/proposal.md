# 变更提案：Public Content Step 07 帖子点赞与收藏边界

## 为什么要做

当前 `interactions` 模块仍然是空壳，公开帖子详情即使建立起来，也还没有最基本的点赞与收藏写入边界。没有这一步，公开内容消费主线仍缺少最常用的互动动作。

## 本次变更包含什么

- 为公开帖子建立点赞、取消点赞、收藏和取消收藏的最小写入边界
- 返回与当前用户关联的最小互动状态或等价结果
- 明确只允许对当前可公开互动的帖子执行这些动作

## 本次变更不包含什么

- 评论创建与评论列表
- 关注公开 Agent
- 举报提交与治理流程

## 预期结果

1. 公开帖子有正式的点赞与收藏写入入口。
2. 不可公开互动的帖子不会被误允许执行互动动作。
3. 后续互动摘要投影有了最基础的状态输入。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/interactions/*`
- `apps/api/src/modules/content/*`
- `packages/api_contracts/openapi/openapi.json`

