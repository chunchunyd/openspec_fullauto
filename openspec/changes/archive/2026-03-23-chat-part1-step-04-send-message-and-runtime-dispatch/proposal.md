# 变更提案：Chat Part1 Step 04 发送消息与 Runtime Dispatch

## 为什么要做

在 private chat 的会话、消息和任务锚点建立之后，真正把培养皿从“可读”推进到“可用”的关键一步，是让用户能够发送文本消息并进入 runtime 调用主链路。

如果没有这一步：

- `chat` 只能展示历史，无法形成真实训练与协作入口
- runtime 边界仍停留在架构说明层，无法被 `apps/api` 的业务模块正式消费
- 后续流式回流、assistant 消息落地和失败重试都没有稳定起点

因此 `chat-part1` 需要先单独拆出“发送用户文本并发起 runtime dispatch”，避免把流式、失败和重试一起塞进同一个 change。

## 本次变更包含什么

本次变更聚焦 private chat 的发送与 dispatch 主线，范围包括：

- 为 owner-scoped private chat 建立文本发送接口
- 在发送时创建或复用会话、持久化用户消息并创建统一 Agent task
- 通过 `libs/agent-runtime` 的共享 provider 发起 runtime 调用
- 返回可供后续流式和结果读取继续消费的受控 accepted 结果

## 本次变更不包含什么

本次变更不包含以下内容：

- 流式事件回流或对外 stream 接口
- assistant 消息最终持久化
- 失败重试入口
- public AI IP 私聊
- 常用指令、快捷任务或多模态消息

## 预期结果

完成后，项目应具备以下结果：

1. 已登录 owner 可以向自己的 private Agent 发送文本消息
2. `chat` 可以通过共享 runtime provider 发起正式 dispatch，而不是在业务模块中直连 transport
3. 后续流式、结果落地和重试都能围绕同一条 send 主线继续演进

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `libs/agent-runtime/*`
- `packages/agent_runtime_contracts/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`
