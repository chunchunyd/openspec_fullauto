# 任务拆解：Chat Hardening Step 12 Assistant 已落库补偿去除 Completion Payload 依赖

## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-12-assistant-present-recovery-without-completion-payload` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/chat-hardening-step-12-assistant-present-recovery-without-completion-payload` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [ ] 确认当前 step 只收口 assistant 已落库场景下的 recovery 去耦，不混入 `runtimeTaskId` 缺失契约修复
- [ ] 阅读前一步 finalize 目标态设计、最新 review 报告与当前 `tryRecoverFinalization` 分支，确认阻塞点集中在 `MESSAGE_COMPLETED` payload 依赖

## 2. Recovery 分支拆路

- [ ] 将 polling recovery 拆成“assistant 缺失，需要 completion payload 创建消息”和“assistant 已存在，只需补剩余读模型”两条受控分支
- [ ] 在 assistant 已存在时移除对 runtime completion payload 的硬依赖，直接进入 content-free reconcile

## 3. Durable State 与日志

- [ ] 明确 assistant 已存在分支以平台 durable state 为补偿真相源，不再尝试覆写既有 assistant 正文
- [ ] 为“assistant 已存在但 payload 缺失仍继续补偿”“assistant 缺失且无 payload 无法创建消息”等关键路径补齐必要日志和错误上下文

## 4. 验证与测试

- [ ] 为 assistant 已存在且 runtime 仅返回终态事件的补偿场景补齐回归测试
- [ ] 为 assistant 已存在但 completion payload 缺失时仍能补齐剩余目标态的场景补齐回归测试
- [ ] 为 assistant 缺失且没有 completion payload 时仍拒绝伪造消息的场景补齐回归测试
- [ ] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [ ] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/chat-hardening-step-12-assistant-present-recovery-without-completion-payload` merge 回 `series/chat-hardening`，保留实现分支上的阶段性提交历史
- 说明：`series/chat-hardening -> dev` 不在本 change 内执行，该操作由人工负责
