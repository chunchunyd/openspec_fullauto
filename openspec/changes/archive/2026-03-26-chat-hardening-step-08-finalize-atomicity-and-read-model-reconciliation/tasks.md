# 任务拆解：Chat Hardening Step 08 Finalize 原子收口与读模型补偿

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-08-finalize-atomicity-and-read-model-reconciliation` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/chat-hardening-step-08-finalize-atomicity-and-read-model-reconciliation` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 finalize 原子性与读模型补偿，不混入 task-events HTTP 契约或新的验收链清理
- [x] 阅读 `chat-hardening` step-06 的恢复逻辑、当前 `finalizeTask` / `tryRecoverFinalization` / `chat.task-events` 测试，确认部分失败窗口集中在 assistant 已落库但后续状态未收口

## 2. Finalize 收口主线

- [x] 将 assistant 消息写入、触发用户消息状态更新和会话最近活跃时间修复收敛到单个受控 finalize / reconcile 入口，避免顺序写入留下半成功裂缝
- [x] 让重复 finalize 既不会重复生成 assistant 消息，也不会因为 assistant 已存在而跳过剩余读模型修复

## 3. Polling 恢复与日志

- [x] 调整 polling 恢复判断，不再仅以 assistant 消息是否存在视为 finalize 已完成；当用户消息状态或会话读模型未收口时仍继续补偿
- [x] 为”进入恢复路径””识别到部分收口””补偿失败”补齐必要的结构化日志与错误上下文

## 4. 验证与测试

- [x] 为 assistant 已创建但用户消息状态未完成、assistant 已创建但会话最近活跃时间未更新、重复轮询幂等和正常完成主线补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `fix/chat-hardening-step-08-finalize-atomicity-and-read-model-reconciliation` merge 回 `series/chat-hardening`，保留实现分支上的阶段性提交历史
- 说明：`series/chat-hardening -> dev` 不在本 change 内执行，该操作由人工负责
