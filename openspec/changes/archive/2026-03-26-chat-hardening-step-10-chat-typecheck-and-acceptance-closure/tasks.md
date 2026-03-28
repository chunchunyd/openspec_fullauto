# 任务拆解：Chat Hardening Step 10 Chat 类型校验与验收链收口

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-10-chat-typecheck-and-acceptance-closure` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/chat-hardening-step-10-chat-typecheck-and-acceptance-closure` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 chat 成功响应元数据的导出与验收链，不混入新的 runtime 语义或全仓库类型债务治理
- [x] 阅读本轮 `chat-hardening` review 报告、当前 chat DTO / OpenAPI 导出结果和 chat 相关测试桩，确认 drift 集中在 success envelope 标量字段与 task metadata 夹具

## 2. DTO 与导出源收口

- [x] 修正 chat 成功响应 DTO 的标量字段声明，避免 `success` 这类布尔字段在共享 OpenAPI 中退化为 `type: object`
- [x] 对齐 send / retry / task-events 成功响应里的 task metadata 字段表达，使 `runtimeTaskId`、`parentTaskId`、失败信息等字段在 DTO 与导出契约中保持稳定形状

## 3. 验证链与夹具收口

- [x] 更新 chat 相关测试桩、fixture builder 或等价辅助方法，使 `AgentTaskInfo` / `TaskInfoDto` mock 与当前类型定义一致，不再依赖不安全断言掩盖字段漂移
- [x] 执行 `openapi-export` 并校验 `packages/api_contracts/openapi/openapi.json` 中 chat 成功响应的标量字段与 task metadata 字段已对齐
- [x] 重新执行 chat-hardening 相关 Jest 与 TypeScript 验收，并明确区分本 step 直接引入的问题与仓库基线遗留问题

## 4. 文档与验收说明

- [x] 如 chat 响应契约或验收命令说明发生变化，更新 `apps/api/README.md` 或等价模块文档（本次无文档变更）
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的 chat-local 类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令（本次修改已有测试夹具，无需新增头注释）

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `fix/chat-hardening-step-10-chat-typecheck-and-acceptance-closure` merge 回 `series/chat-hardening`，保留实现分支上的阶段性提交历史
- 说明：`series/chat-hardening -> dev` 不在本 change 内执行，该操作由人工负责
