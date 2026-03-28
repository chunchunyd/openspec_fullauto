# 变更提案：Public Content Step 09 关注公开 Agent 边界

## 为什么要做

需求文档里的公开 AI IP 主线要求用户能够关注公开 Agent。当前仓库虽已有 Agent 公开可见性基础，但还没有正式的关注关系边界，因此需要单独补一个小 step。

## 本次变更包含什么

- 建立关注、取消关注公开 Agent 的最小数据模型与 API 边界
- 仅允许对具备公开身份的 Agent 建立关注关系
- 返回与当前用户关联的最小关注结果

## 本次变更不包含什么

- 粉丝列表、关注推荐和增长策略
- 私有 Agent 关注
- 首页基于关注关系的复杂排序

## 预期结果

1. 公开 Agent 有正式的关注与取消关注入口。
2. 私有 Agent 不会被误纳入关注对象。
3. 后续互动摘要与首页消费可以复用这条关系主线。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/interactions/*`
- `apps/api/src/modules/agents/*`
- `packages/api_contracts/openapi/openapi.json`

