# 设计说明：Chat Part1 Step 04 发送消息与 Runtime Dispatch

## 目标

让 owner-scoped private chat 的文本发送正式进入 `apps/api -> libs/agent-runtime -> runtime` 主链路，同时保持平台侧的会话、消息和 task 真相源不被 runtime 侵入。

## 边界

### chat 模块负责

- 校验登录态、owner-scoped Agent 访问权和最小输入合法性
- 创建或复用会话（通过 `ChatRepository.upsertConversation`）
- 持久化用户消息（通过 `ChatRepository.createUserMessage`）
- 创建或复用统一 Agent task 记录（通过 `AgentTasksService.createTask`）
- 调用共享 runtime provider（通过 `AgentRuntimeService.startTask`）
- 返回 accepted 结果而不是伪装成最终 assistant 回复

### runtime 负责

- 回复生成
- 流式事件输出
- 成功/失败状态回流

### 本 step 不负责

- 流式事件投影或对外 stream 接口
- assistant 消息最终落地
- 失败重试入口
- public AI IP 私聊
- 常用指令、快捷任务或多模态消息

## 架构

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ API Layer (apps/api/src/modules/chat)                                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ChatController ──────────► ChatService ──────────► AgentRuntimeService            │
│       │                         │                           │                        │
│       │                         ▼                           │                        │
│       │                  ┌──────────────┐                   │                        │
│       │                  │   ChatRepo   │                   │                        │
│       │                  │  (Prisma)    │                   │                        │
│       │                  └──────────────┘                   │                        │
│       │                         │                           │                        │
│       │                         ▼                           ▼                        │
│       │                  ┌──────────────┐      ┌─────────────────────────┐           │
│       │                  │ Conversation │      │    AgentTasksService   │           │
│       │                  │   Message    │      │     (Unified Task)     │           │
│       │                  └──────────────┘      └─────────────────────────┘           │
│       │                                                     │                        │
│       │                                                     ▼                        │
│       │                                          ┌─────────────────────────┐          │
│       │                                          │   AgentTasksRepository  │          │
│       │                                          │       (Prisma)          │          │
│       │                                          └─────────────────────────┘          │
│       │                                                                                │
│       ▼                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────────┐    │
│  │ Response: SendMessageSuccessResponse                                          │    │
│  │ {                                                                             │    │
│  │   success: true,                                                              │    │
│  │   conversation: { id, agentId, ownerId, ... },                                │    │
│  │   message: { id, content, status: PENDING, ... },                             │    │
│  │   task: { id, taskType: CHAT_REPLY, status: QUEUED, runtimeTaskId?, ... },   │    │
│  │   isDuplicate: boolean                                                        │    │
│  │ }                                                                             │    │
│  └──────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Runtime Layer (libs/agent-runtime)                                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  AgentRuntimeService ──────► AgentRuntimeProvider ──────► Mock/GRPC Provider       │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Runtime (Future Go Service / Mock HTTP)                                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  - Prompt orchestration                                                             │
│  - Model routing                                                                    │
│  - Context assembly                                                                 │
│  - Tool calling                                                                     │
│  - Event output (streaming)                                                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 关键流程

### POST /chat/send

1. **请求验证**：校验登录态（AuthGuard）、输入内容（非空、长度限制）
2. **Agent 访问权验证**：验证用户是否拥有目标 Agent
3. **会话创建或复用**：通过 `upsertConversation` 确保同一 owner 与 private Agent 只有一个主会话
4. **用户消息持久化**：创建 `Message` 记录，状态为 `PENDING`
5. **任务记录创建**：创建统一 `AgentTask` 记录，支持幂等性
6. **Runtime Dispatch**：通过共享 provider 发起 runtime 调用
7. **返回结果**：返回 accepted 结果，包含会话、消息和任务锚点

### 幂等性控制

- 客户端可提供 `idempotencyKey` 用于去重
- 若未提供，服务端根据 `message.id` 生成：`chat:reply:{messageId}`
- 重复请求返回原有任务结果，`isDuplicate: true`

## 共享契约

使用 `@nenggan/agent_runtime_contracts` 中定义的：

- `AgentTaskRequestDto`：任务请求 payload
- `AgentTaskType.CHAT_REPLY`：任务类型枚举
- `BizRef`：业务对象引用
- `ContextRef`：上下文引用

## 约束

- `chat` 模块不得在 controller / service 中直接拼 gRPC 或 mock-http transport 细节
- 发送接口返回的是"已受理并已进入统一任务主线"，而不是最终 assistant 回复内容
- 若现有 runtime contract 缺少 chat 所需最小字段，应优先补共享 contract，而不是在 `apps/api` 内自造平行 payload
- runtime 访问统一经由共享 provider，而不是在 `chat` 模块直接接 transport

## 失败场景

| 场景 | 处理方式 | HTTP 状态码 |
|------|----------|-------------|
| 未登录 | AuthGuard 拦截 | 401 |
| Agent 不存在 | 返回 AGENT_NOT_FOUND | 404 |
| Agent 非用户所有 | 返回 ACCESS_DENIED | 403 |
| 内容为空 | 返回 EMPTY_CONTENT | 400 |
| 内容过长 | 返回 CONTENT_TOO_LONG | 400 |
| Runtime dispatch 失败 | 标记任务失败，仍返回成功（消息已持久化） | 200 |
| 重复提交 | 返回原有任务结果 | 200 |

## 数据模型

### Conversation（会话）

- `id`：会话 ID
- `ownerId`：所有者用户 ID
- `agentId`：Agent ID
- `lastActiveAt`：最后活跃时间
- `createdAt`：创建时间
- 唯一约束：`(ownerId, agentId)`

### Message（消息）

- `id`：消息 ID
- `conversationId`：会话 ID
- `senderType`：发送者类型（USER / ASSISTANT）
- `content`：消息内容
- `status`：消息状态（PENDING / SENT / DELIVERED / FAILED）
- `createdAt`：创建时间

### AgentTask（统一任务）

- `id`：任务 ID
- `taskType`：任务类型（CHAT_REPLY）
- `status`：任务状态（QUEUED / RUNNING / STREAMING / SUCCEEDED / FAILED / CANCELLED）
- `actorUserId`：发起用户 ID
- `targetAgentId`：目标 Agent ID
- `bizType`：业务类型（MESSAGE）
- `bizId`：业务对象 ID（消息 ID）
- `idempotencyKey`：幂等键
- `inputPayload`：输入 payload（JSON）
- `errorCode`：错误码（失败时）
- `errorMessage`：错误消息（失败时）
- `createdAt`、`updatedAt`：时间戳
