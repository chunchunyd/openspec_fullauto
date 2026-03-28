# 任务拆解：Chat Part1 Step 01 会话与消息数据模型基线

## 1. 实施前门禁

- [x] 如果 `dev-chat-part1` 不存在，则从最新 `dev` 切出 `dev-chat-part1`（注：Git 不允许 `dev/chat/part1`，因为 `dev` 已存在）
- [x] 从 `dev-chat-part1` 切出 `feat/chat-part1-step-01-session-and-message-data-model-baseline`
- [x] 阅读现有 `openspec/specs/chat/spec.md`、`openspec/specs/repository-structure/spec.md` 与 `docs/current-repository-architecture.md`
- [x] 确认当前 step 只建立 private chat 的会话与消息锚点，不混入读取接口、发送接口、runtime 调用和 public AI IP 会话

## 2. 数据模型与持久化锚点

- [x] 为 owner-scoped private Agent 单聊补齐最小会话 model、enum 与唯一性约束
- [x] 为用户消息与 assistant 消息补齐最小消息 model、发送方类型与基础状态字段
- [x] 明确最近活跃时间、审计时间戳和会话-消息关联关系，避免后续列表与历史读取再造字段

## 3. API 模块基线

- [x] 在 `apps/api/src/modules/chat` 建立最小 repository / service / module 落位
- [x] 明确 `chat` 模块负责会话、消息与业务状态，不直接承担 gRPC/HTTP runtime transport 细节
- [x] 复用现有 `auth` / `agents` 边界，不在 `chat` 内部复制 owner 校验真相源

## 4. 文档与注释

- [x] 更新 `apps/api/README.md` 或等价模块文档，说明 private chat 基础锚点和当前非目标
- [x] 对会话唯一性、消息发送方类型和最小状态边界补必要注释

## 5. 验证与测试

- [x] 为会话创建/复用规则、消息持久化边界和基础映射补单元测试或等价验证
- [x] 运行 Prisma generate / schema 校验与 `apps/api` 相关测试，确认新模型可被 `chat` 模块稳定消费
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/chat-part1-step-01-session-and-message-data-model-baseline` squash merge 回 `dev-chat-part1`；不在本 change 内执行 `dev-chat-part1 -> dev`，该操作由人工负责
