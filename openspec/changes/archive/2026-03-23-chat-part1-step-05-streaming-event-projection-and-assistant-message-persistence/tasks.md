# 任务拆解：Chat Part1 Step 05 流式事件投影与 Assistant 消息落地

## 1. 实施前门禁

- [x] 同步最新 `dev-chat-part1`
- [x] 从 `dev-chat-part1` 切出 `feat/chat-part1-step-05-streaming-event-projection-and-assistant-message-persistence`
- [x] 确认 `chat-part1-step-04-send-message-and-runtime-dispatch` 已完成或达到可复用状态
- [x] 确认当前 step 只处理流式事件投影与 assistant 消息落地，不混入手动重试、public AI IP 私聊和 push/未读能力

## 2. 平台侧事件锚点与流式读取

- [x] 检查平台侧是否已经存在可复用的 append-only task 事件锚点；若没有，则先补 chat 当前需要的最小受控事件投影层
  - 复用 `AgentTask` 作为任务锚点，通过 `bizType` + `bizId` 关联消息
  - 新增 `ChatEventType` 枚举定义受控的 chat 语义事件类型
  - 新增 `ChatTaskStatus` 枚举定义受控的 chat 任务状态
- [x] 建立 owner-scoped 的 chat 流式读取接口或等价事件读取入口
  - 新增 `GET /chat/tasks/:taskId/events` 端点
  - 通过会话所有权验证用户访问权限
  - 支持 `afterSeq` 参数用于断点续传
- [x] 将 runtime 事件映射为 chat 可消费的受控语义，而不是直接泄露 provider 内部事件结构
  - 新增 `projectRuntimeEventToChatEvent()` 方法
  - 新增 `mapRuntimeEventTypeToChatEventType()` 方法
  - 只暴露 chat 相关事件，隐藏 tool calls、moderation 等内部事件

## 3. assistant 消息最终落地

- [x] 在 runtime 成功完成后落地 assistant 消息，并保持与会话、触发消息和任务锚点的关联
  - 新增 `finalizeTask()` 方法
  - 新增 `createAssistantMessageWithIdempotency()` repository 方法
- [x] 刷新会话的最近消息摘要与最近活跃时间
  - 在 `finalizeTask()` 中调用 `updateConversationLastActive()`
  - 同时更新用户消息状态为 `COMPLETED`
- [x] 防止重复事件或乱序回流导致重复 assistant 消息落地
  - 在 `Message` 模型新增 `idempotencyKey` 字段（唯一约束）
  - 使用 `assistant:{taskId}` 格式作为幂等键
  - 通过数据库唯一约束确保消息只落地一次

## 4. 文档与设计说明

- [x] 补 `design.md`，说明 runtime 事件到 chat 结果的投影边界与最终落地规则
- [x] 为新增接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档，说明 chat 流式读取和 assistant 消息落地的职责

## 5. 验证与测试

- [x] 为 owner-scoped 事件读取、assistant 消息最终落地和重复事件去重补集成测试或等价验证
- [x] 验证未授权用户无法消费他人的 chat 流式结果
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/chat-part1-step-05-streaming-event-projection-and-assistant-message-persistence` squash merge 回 `dev-chat-part1`
- 说明：`dev-chat-part1 -> dev` 不在本 change 内执行，该操作由人工负责
