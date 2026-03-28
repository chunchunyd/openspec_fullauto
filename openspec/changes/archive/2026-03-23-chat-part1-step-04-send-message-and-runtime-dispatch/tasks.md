# 任务拆解：Chat Part1 Step 04 发送消息与 Runtime Dispatch

## 1. 实施前门禁

- [x] 同步最新 `dev-chat-part1`
- [x] 从 `dev-chat-part1` 切出 `feat/chat-part1-step-04-send-message-and-runtime-dispatch`
- [x] 阅读现有 `openspec/specs/chat/spec.md`、`openspec/specs/agent-runtime-boundary/spec.md` 和 `openspec/specs/agent-tasks/spec.md`
- [x] 确认当前 step 只处理文本发送与 runtime dispatch，不混入流式回流、assistant 消息最终落地和失败重试

## 2. runtime 契约与 dispatch 前置检查

- [x] 检查 `libs/agent-runtime` 与 `packages/agent_runtime_contracts` 是否已经具备 chat 发送所需的最小 taskType / payload / error 语义；若不足，优先补共享契约而不是在 `chat` 内发明 app-local payload
- [x] 定义发送接口 DTO、幂等键或等价重复提交控制字段
- [x] 保持 runtime 访问统一经由共享 provider，而不是在 `chat` 模块直接接 gRPC / HTTP transport

## 3. 文本发送与任务创建

- [x] 建立 owner-scoped private chat 的文本发送接口
- [x] 在发送时创建或复用会话、持久化用户消息并创建统一 Agent task 记录
- [x] 发起 runtime dispatch，并返回受控 accepted 结果而不是伪装成最终 assistant 回复

## 4. 文档与设计说明

- [x] 补 `design.md`，说明发送、持久化、task 创建和 runtime dispatch 的边界关系
- [x] 为新增接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档，说明发送入口和当前非目标

## 5. 验证与测试

- [x] 为发送成功、输入校验失败、owner 越权和重复提交场景补集成测试或等价验证
- [x] 验证 `chat` 模块不会在业务层直接依赖 transport 细节
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/chat-part1-step-04-send-message-and-runtime-dispatch` squash merge 回 `dev-chat-part1`
- 说明：`dev-chat-part1 -> dev` 不在本 change 内执行，该操作由人工负责
