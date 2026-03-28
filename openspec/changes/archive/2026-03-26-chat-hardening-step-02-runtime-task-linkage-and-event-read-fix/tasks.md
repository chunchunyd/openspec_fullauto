# 任务拆解：Chat Hardening Step 02 Runtime Task 关联与事件读取修复

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-02-runtime-task-linkage-and-event-read-fix` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/chat/spec.md`、`openspec/specs/agent-tasks/spec.md` 与 `openspec/specs/agent-runtime-boundary/spec.md`
- [x] 确认当前 step 只修复平台 task 与 runtime task 的关联和读取链路，不混入 assistant 最终落地或失败重试收口

## 2. 共享边界与持久化锚点检查

- [x] 检查 `libs/agent-runtime`、`packages/agent_runtime_contracts` 与 `apps/api/src/modules/agent-tasks` 是否已经提供可复用的 runtime task 引用承载点；若不足，优先补齐共享契约或统一任务层
- [x] 为平台 `AgentTask` 保留 runtime task 标识或等价映射字段，避免 runtime 标识只在发送返回值中短暂存在

## 3. 发送与读取主线修复

- [x] 调整 chat 发送后的任务更新逻辑，在 dispatch 成功后持久化 runtime task 关联
- [x] 修正任务事件读取主线，确保平台通过受控映射查询 runtime 任务而不是错误复用平台 task id
- [x] 明确 runtime 映射缺失、runtime 任务不存在与平台任务不存在的差异化错误语义

## 4. 验证与测试

- [x] 为发送成功后持久化 runtime task 关联、事件读取命中正确 runtime task、映射缺失场景补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `fix/chat-hardening-step-02-runtime-task-linkage-and-event-read-fix` squash merge 回 `series/chat-hardening`
- `series/chat-hardening -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

