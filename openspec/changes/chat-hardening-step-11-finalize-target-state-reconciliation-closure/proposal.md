# 变更提案：Chat Hardening Step 11 Finalize 目标态补偿收口

## 为什么要做

本轮 `chat-hardening` 验收确认，step-08 虽然已经不再把“assistant 消息已存在”直接视为 finalize 完成，但当前 duplicate finalize / polling recovery 的早退条件仍然主要盯着 `userMessage.status`。这会让“assistant 已落库、user message 已完成、但 conversation 最近活跃时间或平台 task 成功态还没补齐”的半成功窗口继续漏补，重新制造会话排序和任务终态的裂缝。

这一步继续沿用 `chat-hardening` 作为 series prefix，只收口 finalize 的完整目标态补偿，不再混入 completion payload 依赖拆解或 task-events 的无 runtime 链接契约修复。

## 本次变更包含什么

- 将 duplicate finalize / polling recovery 的完成判定升级为完整目标态检查，至少覆盖 assistant 消息、触发用户消息完成态、conversation 最近活跃时间或等价排序读模型，以及平台 task 成功态
- 收紧 finalize / reconcile 主线，使重复 finalize 只有在完整目标态已经达成时才允许 early return
- 为“assistant 已存在且 user message 已完成，但 conversation / task 仍未收口”的半成功场景补齐回归测试与必要日志

## 本次变更不包含什么

- assistant 已存在时彻底去除对 runtime `MESSAGE_COMPLETED` payload 的恢复依赖
- `runtimeTaskId` 缺失时的 task-events 终态语义与 HTTP 契约修正
- 新的后台补偿 worker、定时扫描器或 schema 迁移

## 预期结果

1. duplicate finalize 不会再因为单一状态位已对齐就过早退出。
2. 历史上已经落入“assistant 已存在但 conversation / task 未收口”的数据，可以在后续 polling 中被继续补齐。
3. 会话列表排序、历史消息完成态和平台 task 成功态重新回到同一条受控完成主线。

## Capabilities

### New Capabilities

- 无

### Modified Capabilities

- `chat`: 收紧 polling finalize 的完成判定，要求 assistant、用户消息、会话读模型和平台 task 一起达到最终目标态

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- 如平台 task 成功态更新路径需要补辅助测试，可能影响 `apps/api/src/modules/agent-tasks/*`
