# 任务拆解：Chat Hardening Step 11 Finalize 目标态补偿收口

## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-11-finalize-target-state-reconciliation-closure` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/chat-hardening-step-11-finalize-target-state-reconciliation-closure` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [ ] 确认当前 step 只收口 finalize 的完整目标态补偿，不混入 completion payload 依赖拆解或 `runtimeTaskId` 缺失契约修复
- [ ] 阅读 `chat-hardening` step-08、最新 review 报告与当前 `finalizeTask` / `tryRecoverFinalization` 流程，确认早退条件遗漏了 conversation / task 目标态

## 2. Finalize 目标态判定

- [ ] 将 finalize 完成态收敛为完整目标态检查，至少覆盖 assistant 消息、user message 完成态、conversation 最近活跃时间或等价排序读模型，以及平台 task 成功态
- [ ] 调整 duplicate finalize 的 early return 条件，使其只在完整目标态已经达成时返回，避免因单一状态位达成而跳过剩余补偿

## 3. Recovery 与幂等补偿

- [ ] 让 polling recovery 复用同一套目标态缺口判断，确保“assistant 已存在且 user message 已完成，但 conversation / task 未收口”的场景仍继续补偿
- [ ] 为进入缺口补偿、完成收口与补偿失败补齐必要的结构化日志和错误上下文

## 4. 验证与测试

- [ ] 为 assistant 已存在且 user message 已完成、但 conversation / task 仍未收口的半成功场景补齐回归测试
- [ ] 为 duplicate finalize 在完整目标态成立时才 early return 的行为补齐回归测试
- [ ] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [ ] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/chat-hardening-step-11-finalize-target-state-reconciliation-closure` merge 回 `series/chat-hardening`，保留实现分支上的阶段性提交历史
- 说明：`series/chat-hardening -> dev` 不在本 change 内执行，该操作由人工负责
