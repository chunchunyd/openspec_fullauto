# 变更提案：Public Content Step 10 举报提交基线

## 为什么要做

公开内容与互动主线建立后，还需要一个最小治理入口。当前仓库没有举报提交边界，因此帖子、评论和公开 Agent 的治理链路还缺少正式入口。

## 本次变更包含什么

- 建立对帖子、评论和公开 Agent 的最小举报提交边界
- 记录举报对象、理由和提交时间等最小治理输入
- 明确“举报已提交”不等于“对象已被判定违规”

## 本次变更不包含什么

- 举报审核、判定和执行结论
- 管理端处置界面
- 复杂风控策略与批量治理

## 预期结果

1. 帖子、评论和公开 Agent 都有正式的举报提交入口。
2. 举报提交可以成为后续 moderation 流程的稳定输入。
3. 客户端不会把举报提交误解为即时判定结果。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/interactions/*`
- `apps/api/src/modules/moderation/*`
- `packages/api_contracts/openapi/openapi.json`

