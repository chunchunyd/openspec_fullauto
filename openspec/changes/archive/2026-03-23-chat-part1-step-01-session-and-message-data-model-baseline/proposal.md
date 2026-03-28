# 变更提案：Chat Part1 Step 01 会话与消息数据模型基线

## 为什么要做

`apps/api/src/modules/chat` 当前仍是空模块，但首期培养皿链路至少要有“用户与自己私有 Agent 的单聊锚点”。如果一开始不先落会话与消息的持久化模型：

- 会话列表、历史消息和最近活跃排序都没有稳定真相源
- runtime 回流结果没有明确的 assistant 消息落点
- 统一 Agent task、失败状态和重试语义会被迫依赖内存态或临时字段

因此 `chat-part1` 的第一步应先把 owner-scoped private chat 的会话与消息数据模型打稳，再继续叠加读取、发送和流式回流能力。

## 本次变更包含什么

本次变更聚焦 private chat 的基础持久化锚点，范围包括：

- 为 owner-scoped private Agent 单聊建立最小会话模型
- 为用户消息与后续 assistant 消息建立最小消息模型
- 明确会话唯一性、消息发送方类型和最小状态字段
- 在 `apps/api` 中建立 `chat` 模块的 repository / service 基线落位

## 本次变更不包含什么

本次变更不包含以下内容：

- 会话列表或历史消息读取接口
- 文本消息发送接口
- runtime 调用、流式回流或任务创建
- public AI IP 私聊边界
- 未读计数、已读回执、附件或多模态消息

## 预期结果

完成后，项目应具备以下结果：

1. `chat` 不再只有空 `Module`，而是拥有可复用的会话与消息持久化锚点
2. 后续会话列表、历史消息、runtime 结果投影和失败重试都有统一落点
3. private chat 不需要在后续 step 中重复发明另一套并行消息模型

## 影响范围

本次变更主要影响：

- `prisma/schema.prisma`
- `prisma/migrations/*`
- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `apps/api/README.md`
