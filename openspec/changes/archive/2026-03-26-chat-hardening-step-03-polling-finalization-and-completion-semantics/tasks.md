# 任务拆解:Chat Hardening Step 03 轮询完成落地与完成语义修复

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪(若不存在则从最新 `dev` 创建)
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-03-polling-finalization-and-completion-semantics` 实现分支,并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/chat/spec.md`、`openspec/specs/agent-tasks/spec.md` 与当前 `chat` 事件读取实现
- [x] 确认当前 step 只修正轮询完成语义和 assistant 落地主线,不混入 dispatch 失败与重试收口

## 2. 轮询语义与结果投影

- [x] 收紧 `getTaskEvents` 的完成判定规则,明确区分"任务终态""当前页无新增事件"和"仍可继续轮询"
- [x] 避免继续使用 `!hasMore` 近似代表任务完成,改为基于受控终态事件或等价投影输出完成语义

## 3. assistant 消息落地与会话刷新

- [x] 让当前公开轮询主线在确认任务成功完成后触发 assistant 消息最终落地,而不是只在内部 stream 路径上执行
- [x] 确保 assistant 消息落地具备幂等保护,并会同步刷新会话最近消息摘要与最近活跃时间

## 4. 验证与测试

- [x] 为"暂无新事件但任务未完成""任务成功完成后 assistant 消息落地""重复读取不重复落地"补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收,确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收,确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件,测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `fix/chat-hardening-step-03-polling-finalization-and-completion-semantics` squash merge 回 `series/chat-hardening`
- `series/chat-hardening -> dev` 的最终回合并由人工负责,不纳入本 change 的执行范围

