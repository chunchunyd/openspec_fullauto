# 任务拆解：Chat Part1 Step 03 会话列表与历史消息读取

## 1. 实施前门禁

- [x] 同步最新 `dev-chat-part1`
- [x] 从 `dev-chat-part1` 切出 `feat/chat-part1-step-03-session-list-and-history-read-model`
- [x] 确认 `chat-part1-step-01-session-and-message-data-model-baseline` 已完成或达到可复用状态
- [x] 确认当前 step 只处理会话列表与历史消息读取，不混入发送接口、流式回流和 public AI IP 会话

## 2. owner-scoped 读取主线

- [x] 建立会话列表读取接口，并返回会话标识、对应 Agent 基础信息、最近消息摘要和最近活跃时间
- [x] 建立历史消息分页读取接口，并按稳定顺序返回用户消息与 assistant 消息
- [x] 让会话列表基于最近活跃时间排序，避免客户端自行拼接排序语义

## 3. 鉴权、契约与边界

- [x] 复用现有 auth guard / current user 注入边界，确保只返回当前 owner 可读取的 private 会话
- [x] 拒绝通过会话标识越权读取他人的 private chat 历史
- [x] 为新增接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`

## 4. 文档与注释

- [x] 更新 `apps/api/README.md` 或等价模块文档，说明培养皿读取主线和本 step 的非目标
- [x] 对分页顺序、最近消息摘要生成和 owner-scoped 读取边界补必要注释

## 5. 验证与测试

- [x] 为会话列表读取、历史消息分页和越权访问场景补集成测试或等价验证
- [x] 验证接口不会泄露不属于当前用户的 private Agent 会话
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/chat-part1-step-03-session-list-and-history-read-model` squash merge 回 `dev-chat-part1`
- 说明：`dev-chat-part1 -> dev` 不在本 change 内执行，该操作由人工负责
