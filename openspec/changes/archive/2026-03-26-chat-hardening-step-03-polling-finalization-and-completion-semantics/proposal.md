# 变更提案：Chat Hardening Step 03 轮询完成落地与完成语义修复

## 为什么要做

当前公开的 chat 回复读取主线主要是轮询 `GET /chat/tasks/:taskId/events`，但 assistant 消息落地却只挂在内部 stream 路径上。同时轮询结果又把 `hasMore` 近似当成完成语义，容易把“暂无新事件”误判成“任务已完成”。

如果不修这一步：

- 轮询主线拿不到稳定的 assistant 最终消息落地
- 客户端会收到不可靠的 `isCompleted` 或等价完成判断
- 历史消息主线与事件主线会继续分叉

## 本次变更包含什么

- 让当前公开的轮询读取主线具备受控的完成判定语义
- 在轮询确认任务成功完成后落地 assistant 消息，并刷新会话摘要
- 统一 chat 对外返回的完成、进行中与暂时无新增事件的语义

## 本次变更不包含什么

- dispatch bootstrap 失败与消息失败状态一致性修复
- 重试门禁和原始失败消息闭环修复
- SSE、WebSocket 或推送通知形态的对外实时通道

## 预期结果

1. 轮询主线可以驱动 assistant 消息正式落地。
2. “暂无新事件”和“任务已完成”会被明确区分。
3. 会话历史、会话摘要和任务事件主线在成功场景下重新对齐。

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`

