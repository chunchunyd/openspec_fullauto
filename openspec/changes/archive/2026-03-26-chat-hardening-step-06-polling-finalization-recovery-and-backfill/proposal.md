# 变更提案：Chat Hardening Step 06 轮询 finalize 恢复与回填

## 为什么要做

`chat-hardening` 在 step-03 已经建立了“轮询确认完成后落地 assistant 消息”的主线，但验收显示当前实现仍然把 finalize 触发过度绑定在本次 `afterSeq` 结果页里是否恰好出现 `content.completed` 事件。如果 finalize 第一次执行失败，或者客户端恢复轮询时已经越过了完成事件，接口仍可能返回 `isCompleted = true`，却永远不再补落 assistant 消息。

本批 change 继续沿用 `chat-hardening` 作为 series prefix，且这一 step 只收口 polling 路径的 finalize 恢复与消息回填语义。当前 step 复用 step-03 的完成语义和 step-04 的失败收口，不新增后台补偿 worker、独立扫描任务或新的流式协议分支。

## 本次变更包含什么

- 让 polling 主线在 task 已完成但 assistant 消息尚未落地时具备恢复性 finalize / backfill 能力
- 消除 finalize 只能依赖当前结果页命中完成事件的脆弱前提
- 为 finalize 首次失败后恢复、越过完成事件后补落消息等边界补齐回归测试

## 本次变更不包含什么

- dispatch 失败首包状态对齐
- task events 的 DTO、OpenAPI 或前端文档命名清理
- 新的后台补偿扫描器、定时任务或通用消息修复平台

## 预期结果

1. 轮询接口在 task 已完成时可以自恢复地补落 assistant 消息。
2. 客户端即使错过完成事件所在的页，也不会永久停留在“任务完成但历史没消息”的断裂状态。
3. polling 主线会具备更稳定的最终一致性，而不是依赖一次性命中完成事件。

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`

