# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须在 dispatch 失败时返回与持久化状态一致的发送结果

系统必须在 chat dispatch bootstrap 失败后立即返回与最新持久化状态一致的发送结果，而不是继续暴露旧的内存排队态。 The system MUST align the immediate send response with the persisted failure projection after dispatch bootstrap failure.

#### Scenario: dispatch bootstrap 失败后的发送首包

- WHEN 平台已经持久化用户消息并创建 task，但 runtime dispatch bootstrap 失败
- THEN `POST /chat/send` 的响应必须返回与最新持久化结果一致的失败消息状态和失败任务状态
- AND 响应中的失败信息不得继续停留在旧的排队态投影

#### Scenario: 客户端基于首包判断失败可重试

- WHEN 客户端收到一次 dispatch bootstrap 失败的发送响应
- THEN 它必须能够直接从该响应识别失败信息与可重试语义
- AND 不得被迫先额外轮询或重读历史才能知道该消息已经进入失败主线

