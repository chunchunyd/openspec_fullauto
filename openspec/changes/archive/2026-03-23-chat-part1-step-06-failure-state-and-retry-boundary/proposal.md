# 变更提案：Chat Part1 Step 06 失败状态与重试边界

## 为什么要做

private chat 在发送、dispatch 和流式落地打通后，仍然需要一个明确的失败与重试边界，否则培养皿主流程会停留在“能成功时很好看、失败时语义模糊”的状态。

如果没有这一步：

- runtime bootstrap 失败、执行失败和超时失败很难被前后端一致识别
- 用户无法对失败消息进行受控重试
- `chat` 很容易退化为重复点击就重复创建任务的无门禁实现

因此 `chat-part1` 的收口步骤应单独处理失败状态与重试，让 private chat 至少具备最小可恢复能力。

## 本次变更包含什么

本次变更聚焦 private chat 的失败与重试边界，范围包括：

- 为 dispatch 失败、执行失败和超时等结果建立受控失败状态映射
- 在聊天读取结果中返回最小失败信息与是否可重试标识
- 提供 owner-scoped 的手动重试入口
- 约束重试与原始失败消息、原始 task 之间的关联关系

## 本次变更不包含什么

本次变更不包含以下内容：

- public AI IP 私聊
- 常用指令、快捷任务消息
- 高级风控、上下文裁剪和更复杂治理规则
- push 通知、任务取消和通用补偿平台
- chat 之外其他 capability 的失败重试通用化

## 预期结果

完成后，项目应具备以下结果：

1. private chat 失败时有明确、可读、可追踪的状态结果
2. 用户可以对失败消息执行受控手动重试
3. `chat-part1` 作为第一阶段 private chat 主路径，至少具备最小可恢复能力

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`
