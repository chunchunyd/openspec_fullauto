# 变更提案：Chat Hardening Step 05 Dispatch 失败返回态一致性修复

## 为什么要做

`chat-hardening` 在 step-04 已经补上了 dispatch bootstrap 失败时的消息失败状态、任务失败状态和重试闭环，但验收显示 `POST /chat/send` 的即时返回仍可能序列化旧的内存态。结果是数据库里已经是 `FAILED`，客户端首包却还看到 `PENDING` 或 `QUEUED`，必须额外再轮询一次才能知道真实失败。

本批 change 继续沿用 `chat-hardening` 作为 series prefix，且这一 step 只收口发送首包与持久化失败投影之间的一致性问题。当前 step 复用 step-04 已经建立的失败状态语义、失败信息映射和重试门禁，不新增新的后台补偿任务、流式协议或公共 chat 范围扩展。

## 本次变更包含什么

- 对齐 `POST /chat/send` 在 dispatch bootstrap 失败时的即时返回态与持久化失败状态
- 确保返回中的消息状态、任务状态、失败信息和可重试语义可以直接驱动客户端失败 UI
- 为 dispatch 失败首包返回补齐回归测试，避免再次出现“落库已失败、响应仍未失败”的断层

## 本次变更不包含什么

- 轮询主线的 finalize 恢复或 assistant 消息回填
- task events 的 DTO、OpenAPI 或文档契约清理
- public AI IP 私聊、通用补偿平台或取消任务能力

## 预期结果

1. dispatch bootstrap 失败时，客户端首包就能看到与数据库一致的失败结果。
2. 前端不需要依赖额外轮询才能判断这次发送是否已经进入失败可重试状态。
3. step-04 建立的失败闭环会真正延伸到首个 API 返回，而不是只停留在历史读取主线。

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`

