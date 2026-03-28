# 变更提案：Chat Part1 Step 05 流式事件投影与 Assistant 消息落地

## 为什么要做

文本发送和 runtime dispatch 打通之后，private chat 仍然只有“用户消息已受理”，还没有真正可消费的回复过程和最终回复结果。

如果没有这一步：

- 客户端无法以 chat 语义读取流式回复过程
- runtime 事件只能停留在 provider 私有输出，无法成为平台可追踪结果
- assistant 消息没有正式落地，历史消息会停留在“只有用户消息”的半成品状态

因此需要把 runtime 事件投影和 assistant 消息落地拆成单独 step，让 `chat` 在不混入失败重试的前提下先形成完整回复主线。

## 本次变更包含什么

本次变更聚焦回复过程与最终落地，范围包括：

- 为 chat 回复建立平台侧 append-only 事件锚点或等价投影结果
- 提供 owner-scoped 的 chat 流式读取或等价事件读取入口
- 将 runtime 事件映射为受控 chat 语义，而不是直接泄露 provider 内部事件
- 在成功完成后落地 assistant 消息，并刷新会话的最近活跃与最近消息摘要

## 本次变更不包含什么

本次变更不包含以下内容：

- 失败重试入口
- public AI IP 私聊
- 通用事件总线或完整 `event_schema` 平台化治理
- push 通知、未读计数和已读回执
- 常用指令、快捷任务和多模态消息

## 预期结果

完成后，项目应具备以下结果：

1. private chat 可以以 chat 语义读取回复过程，而不是只能依赖 runtime 私有 task 视图
2. 成功完成的回复能够落地为 assistant 消息并回到历史消息主线
3. 后续失败重试和治理能力可以围绕平台侧事件与结果主线继续演进

## 影响范围

本次变更主要影响：

- `prisma/schema.prisma`
- `prisma/migrations/*`
- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `packages/agent_runtime_contracts/*`
- `apps/api/README.md`
