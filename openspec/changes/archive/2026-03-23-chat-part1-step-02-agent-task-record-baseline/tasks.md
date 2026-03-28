# 任务拆解：Chat Part1 Step 02 Agent Task 记录基线

## 1. 实施前门禁

- [x] 同步最新 `dev-chat-part1`
- [x] 从 `dev-chat-part1` 切出 `feat/chat-part1-step-02-agent-task-record-baseline`
- [x] 阅读现有 `openspec/specs/agent-tasks/spec.md`、`openspec/specs/chat/spec.md` 与 `openspec/specs/agent-runtime-boundary/spec.md`
- [x] 确认当前 step 只建立 chat 首次消费的统一 task 记录锚点，不混入 runtime dispatch、事件回流和重试入口

## 2. 统一 task 记录与业务引用

- [x] 为 chat 回复请求补齐最小 Agent task model、状态字段与最小失败信息字段
- [x] 为 task 建立会话、触发消息和目标 Agent 的业务引用，避免 task 变成孤立状态
- [x] 为幂等键、按消息/会话定位 task 和基础更新时间排序建立受控查询语义

## 3. API 侧最小共享入口

- [x] 在 `apps/api` 中建立供 `chat` 后续复用的最小 task repository / service 入口
- [x] 检查是否已存在可复用的共享 task 抽象；若没有，则在当前 step 只补最小入口，不提前扩成覆盖 content / training 的大模块
- [x] 保持 task 记录与 runtime transport 解耦，不在本 step 内直接散落 gRPC / HTTP 调用细节

## 4. 文档与注释

- [x] 更新 `apps/api/README.md` 或等价模块说明，记录 chat 首次消费统一 Agent task 的边界和非目标
- [x] 对 task 与会话/消息业务引用、幂等键和最小失败语义补必要注释

## 5. 验证与测试

- [x] 为 task 创建、重复提交识别、业务引用查询和状态映射补单元测试或等价验证
- [x] 运行 Prisma generate / schema 校验与 `apps/api` 相关测试，确认统一 task 记录可被 `chat` 稳定消费
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/chat-part1-step-02-agent-task-record-baseline` squash merge 回 `dev-chat-part1`
- 说明：`dev-chat-part1 -> dev` 不在本 change 内执行，该操作由人工负责
