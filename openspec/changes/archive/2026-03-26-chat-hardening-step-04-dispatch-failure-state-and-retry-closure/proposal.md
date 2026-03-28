# 变更提案：Chat Hardening Step 04 Dispatch 失败状态与重试闭环修复

## 为什么要做

当前 chat 已经提供失败读取与重试入口，但 dispatch bootstrap 失败时只会把任务标成失败，消息本身却可能保留为旧状态。随后重试门禁又要求消息必须是 `FAILED`，导致一部分真实失败无法进入重试主线。

如果不补这一步：

- dispatch 失败会停留在“任务失败、消息未失败”的不一致状态
- 客户端无法稳定判断消息是否可重试
- chat 第一阶段主路径会继续停留在“理论有重试、实际有失败死角”的状态

## 本次变更包含什么

- 统一 dispatch bootstrap 失败时的消息状态、任务状态和失败信息投影
- 收紧重试门禁，让可重试判断与真实失败状态保持一致
- 为失败返回、历史读取和重试入口补齐一致性测试

## 本次变更不包含什么

- public AI IP 私聊
- 常用指令、快捷任务或多模态消息
- 通用任务补偿平台或取消任务能力

## 预期结果

1. dispatch bootstrap 失败会形成前后端一致的失败语义。
2. 历史消息读取可以稳定返回失败信息与可重试标识。
3. 用户对真实失败消息的手动重试主线能够闭环。

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`

