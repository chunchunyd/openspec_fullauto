# 变更提案：Chat Part1 Step 03 会话列表与历史消息读取

## 为什么要做

在 private chat 的会话、消息和任务锚点建立之后，培养皿首先需要的是稳定的读取主线。

如果没有这一步：

- `apps/mobile` 和后续 admin / test 工具都没有会话列表与历史消息的正式读取入口
- 后续发送、流式和失败重试将缺少可回看的 read model
- private chat 的 owner-scoped 权限边界很容易在控制器层被重复发明

因此 `chat-part1` 的第三步应先把会话列表与历史消息读取拆出来，形成培养皿的最小读取基线。

## 本次变更包含什么

本次变更聚焦 private chat 的读取主线，范围包括：

- 为已登录 owner 提供会话列表读取接口
- 为单个会话提供历史消息分页读取接口
- 返回最近消息摘要、最近活跃时间和最小消息字段
- 明确 owner-scoped 访问边界和分页顺序约束

## 本次变更不包含什么

本次变更不包含以下内容：

- 文本消息发送接口
- runtime 调用和流式回流
- public AI IP 会话读取
- 未读计数、已读回执和跨设备同步细化
- 手动重试入口

## 预期结果

完成后，项目应具备以下结果：

1. 培养皿可以读取 owner-scoped 会话列表和历史消息
2. 会话排序、消息分页和权限边界有正式 API 真相源
3. 后续发送、流式和失败状态都有稳定的读取宿主

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`
