# 变更提案：Chat Hardening Step 08 Finalize 原子收口与读模型补偿

## 为什么要做

`chat-hardening` 在 step-06 已经让 polling 主线能够在“assistant 消息缺失”时恢复 finalize，但本轮验收确认当前 `finalizeTask` 仍按“先写 assistant 消息、再改用户消息状态、再改会话最近活跃时间”的顺序逐步执行。这样一来，只要 assistant 消息已经落库，而后续状态更新或会话读模型更新失败，后续轮询就会因为“assistant 已存在”提前退出，留下永久的半成功裂缝。

这一步继续沿用 `chat-hardening` 作为 series prefix，只收口 finalize 的原子性与读模型补偿，不再混入 task-events HTTP 契约或验收链清理。

## 本次变更包含什么

- 将 assistant 消息落地、触发用户消息状态更新和会话最近活跃时间/摘要修复收敛到同一个受控 finalize/reconcile 主线
- 调整 polling 恢复逻辑，使其不再仅以“assistant 消息是否存在”判断 finalize 已完成
- 为“assistant 已存在但用户消息状态或会话读模型未收口”的部分失败场景补齐回归测试与日志

## 本次变更不包含什么

- `GET /chat/tasks/:taskId/events` 的受控错误 HTTP 契约补齐
- send / retry 响应元数据的导出与类型校验收口
- 新的后台扫描器、定时补偿任务或 public chat 范围扩展

## 预期结果

1. polling 路径在 finalize 部分成功后仍能自恢复地补齐剩余读模型状态。
2. 系统不会因为 assistant 消息已存在而永久放弃用户消息状态和会话最近活跃时间的修复。
3. `chat` 的历史消息主线、失败/完成状态和会话列表摘要在完成路径上重新保持一致。

## Capabilities

### New Capabilities

- 无

### Modified Capabilities

- `chat`: 收紧 polling finalize 的收口语义，要求 assistant 消息、触发用户消息状态和会话读模型一起完成最终一致性修复

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- 如需要抽象仓储事务封装，可能影响 `apps/api/src/modules/chat/chat.repository.ts`
