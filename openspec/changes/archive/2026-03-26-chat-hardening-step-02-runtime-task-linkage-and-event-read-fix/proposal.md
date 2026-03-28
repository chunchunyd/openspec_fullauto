# 变更提案：Chat Hardening Step 02 Runtime Task 关联与事件读取修复

## 为什么要做

当前 chat 发送链路会创建平台 `AgentTask`，也会从 runtime 收到独立的 runtime task 标识，但平台侧没有把二者稳定关联起来。随后事件读取又直接拿平台 task id 去问 runtime，导致真实链路存在错位风险。

如果不补这一步：

- 发送成功后的事件轮询无法稳定命中 runtime 真实任务
- 平台 task 与 runtime task 会长期处于“短暂返回、不可追踪”的半断链状态
- 后续 assistant 消息落地和失败恢复都缺少可靠的任务主线

## 本次变更包含什么

- 为平台 `AgentTask` 与 runtime task 建立稳定关联字段或等价受控映射
- 修正 chat 事件读取主线，让平台通过受控映射访问 runtime 结果，而不是假设两侧 task id 相同
- 补齐发送、查询和任务恢复所需的最小测试与文档

## 本次变更不包含什么

- 轮询完成后自动落地 assistant 消息
- dispatch bootstrap 失败与消息失败状态一致性修复
- 通用 runtime 事件平台化治理

## 预期结果

1. chat 平台 task 能稳定定位其对应的 runtime task。
2. `GET /chat/tasks/:taskId/events` 读取的是与该平台任务真实关联的 runtime 结果。
3. 后续完成语义和失败重试可以围绕同一条任务映射主线继续建设。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/agent-tasks/*`
- `apps/agent-runtime-mock/*`
- `packages/api_contracts/openapi/openapi.json`

