# 任务拆解：Chat Hardening Step 13 Task Events 无 Runtime 链接时保留平台终态语义

## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-13-task-events-terminal-state-preservation-without-runtime-linkage` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/chat-hardening-step-13-task-events-terminal-state-preservation-without-runtime-linkage` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [ ] 确认当前 step 只收口无 runtime 链接时的 task-events 状态语义，不混入 finalize 相关补偿逻辑
- [ ] 阅读 `chat-hardening` step-04、step-05、step-09 和最新 review 报告，确认当前冲突点集中在 `runtimeTaskId` 缺失分支把平台终态压成 `UNKNOWN`

## 2. Task Events 状态语义

- [ ] 调整 `runtimeTaskId` 缺失分支的状态投影，使 `status` / `isCompleted` 优先保留平台 task 已知状态，尤其是 `FAILED` 等终态
- [ ] 保留 `RUNTIME_TASK_NOT_LINKED` 等受控错误字段，但避免它覆盖掉平台 task 已知状态和完成态

## 3. 契约与文档

- [ ] 对齐 service、controller 和 DTO，使无 runtime 链接结果能够同时表达受控错误字段与平台 task 状态语义
- [ ] 执行 `openapi-export` 并更新 `packages/api_contracts/openapi/openapi.json`，确保共享契约能表达 not-linked 与平台状态共存的结果
- [ ] 如 `apps/api/README.md` 已描述 task-events 轮询语义，补充“无 runtime 链接但平台 task 已知终态”这一类结果说明

## 4. 验证与测试

- [ ] 为 dispatch 失败后读取 task-events 的场景补齐回归测试，确认 `FAILED` 终态不会再被压成 `UNKNOWN`
- [ ] 为无 runtime 链接但任务仍处于非终态的场景补齐回归测试，确认受控错误字段与平台状态语义保持一致
- [ ] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [ ] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/chat-hardening-step-13-task-events-terminal-state-preservation-without-runtime-linkage` merge 回 `series/chat-hardening`，保留实现分支上的阶段性提交历史
- 说明：`series/chat-hardening -> dev` 不在本 change 内执行，该操作由人工负责
