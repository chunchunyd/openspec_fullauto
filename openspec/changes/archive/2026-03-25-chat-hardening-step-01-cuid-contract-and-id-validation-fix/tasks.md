# 任务拆解：Chat Hardening Step 01 CUID 契约与 ID 校验修复

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-01-cuid-contract-and-id-validation-fix` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/chat/spec.md`、`openspec/specs/agent-tasks/spec.md` 与 `prisma/schema.prisma`
- [x] 确认当前 step 只修正平台 ID 契约与输入校验，不混入 runtime 关联或失败重试逻辑

## 2. 契约与 DTO 校正

- [x] 盘点 `chat` 模块中所有对会话、消息、任务 ID 的输入校验与 Swagger 描述，找出仍按 UUID 约束的平台主键入口
- [x] 将这些入口统一改成与 Prisma `cuid` 真相源一致的受控校验方式，而不是继续要求 UUID
- [x] 同步更新响应示例、字段说明和错误语义，避免 OpenAPI 继续暗示错误的 ID 格式

## 3. 控制器与读取主线对齐

- [x] 确认历史消息、任务事件读取和失败重试入口都能接受合法 `cuid` 并进入真实业务校验
- [x] 清理控制器层因 UUID 误校验导致的假性 `400`，把越权与不存在场景留给业务层处理

## 4. 验证与测试

- [x] 为会话历史、任务事件和失败重试相关 DTO 或控制器补充 `cuid` 输入通过、非法格式拒绝与业务错误分流测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `fix/chat-hardening-step-01-cuid-contract-and-id-validation-fix` squash merge 回 `series/chat-hardening`
- `series/chat-hardening -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

