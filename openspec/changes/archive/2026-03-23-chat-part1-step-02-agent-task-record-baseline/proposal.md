# 变更提案：Chat Part1 Step 02 Agent Task 记录基线

## 为什么要做

private chat 的文本发送不会停留在本地消息 CRUD，它后面一定会进入统一 runtime 调用、流式回流、失败状态和重试链路。

如果没有先建立 chat 首次消费的 Agent task 记录锚点：

- `chat` 会被迫直接依赖 runtime 私有 task 标识
- 后续 stream、失败和重试无法围绕同一条业务主线追踪
- `content` 等后续能力也更难复用统一的任务语义

因此在 `chat-part1` 中，应先为 chat 落下最小统一 Agent task 记录基线，让 chat 的每次回复请求都能有稳定的平台侧任务锚点。

## 本次变更包含什么

本次变更聚焦 chat 首次消费的统一 Agent task 记录，范围包括：

- 为 chat 回复请求建立最小 Agent task 持久化模型与状态字段
- 为会话、触发消息和 task 之间建立明确业务引用
- 为幂等键、查询入口和最小失败信息建立平台侧锚点
- 在 `apps/api` 中建立供 `chat` 后续复用的最小 task repository / service 入口

## 本次变更不包含什么

本次变更不包含以下内容：

- 文本消息发送接口
- runtime 调用或流式回流
- content / training 等其他能力对统一 task 的正式接入
- append-only 任务事件日志或对外 stream 接口
- 失败重试入口

## 预期结果

完成后，项目应具备以下结果：

1. chat 回复请求可以围绕统一 Agent task 记录进行追踪，而不是只依赖 runtime 私有标识
2. 后续发送、流式、失败和重试都能共用同一条任务主线
3. 统一 Agent task 能力开始在 `apps/api` 中有第一处真实落地入口

## 影响范围

本次变更主要影响：

- `prisma/schema.prisma`
- `prisma/migrations/*`
- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `apps/api/README.md`
