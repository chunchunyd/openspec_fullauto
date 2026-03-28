# 变更提案：Chat Hardening Step 12 Assistant 已落库补偿去除 Completion Payload 依赖

## 为什么要做

最新验收确认，当前 polling recovery 即使已经识别出“assistant 消息已存在但读模型仍未收口”的部分成功状态，后续仍会强依赖 runtime 事件里再次出现 `MESSAGE_COMPLETED` 及其 `content`，才能触发补偿。这让 step-08 / step-11 想解决的半成功场景仍然会在“assistant 已落库、但 runtime 只保留终态事件或 completion payload 缺失”时永久漏补。

这一步继续沿用 `chat-hardening` 作为 series prefix，只收口“assistant 已落库”场景下的补偿去耦，不再混入 `runtimeTaskId` 缺失契约修复。

## 本次变更包含什么

- 将 polling recovery 拆成“assistant 缺失，需要从 runtime completion payload 创建消息”和“assistant 已存在，只需补齐剩余读模型”两条受控分支
- 在 assistant 已存在时，允许系统不依赖 runtime completion payload 继续补 user message / conversation / task 等剩余目标态
- 为“runtime 仅返回终态事件”或“completion payload 缺失”但 assistant 已落库的场景补齐回归测试和日志

## 本次变更不包含什么

- finalize 完整目标态定义本身的扩展或新的事务边界治理
- `runtimeTaskId` 缺失时 task-events 状态与共享 OpenAPI 的终态语义修正
- 新的 runtime transport、push 通道或历史数据批处理补偿工具

## 预期结果

1. assistant 已经落库的情况下，polling recovery 不再依赖 runtime 重放完整 completion payload 才能继续补偿。
2. “assistant 已存在，但剩余读模型未收口”的历史半成功数据，在 runtime 只提供终态事件时仍可被修复。
3. 只有在 assistant 消息确实缺失时，系统才继续要求从 runtime completion payload 提取最终内容。

## Capabilities

### New Capabilities

- 无

### Modified Capabilities

- `chat`: 收紧 polling recovery 的补偿分支，要求 assistant 已落库时可以脱离 runtime completion payload 继续补齐剩余读模型

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- 如恢复语义说明已有模块文档，可能影响 `apps/api/README.md`
