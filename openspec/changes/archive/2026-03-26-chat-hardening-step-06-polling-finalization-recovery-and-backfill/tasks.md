# 任务拆解：Chat Hardening Step 06 轮询 finalize 恢复与回填

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-06-polling-finalization-recovery-and-backfill` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/chat-hardening-step-06-polling-finalization-recovery-and-backfill` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 polling finalize 恢复与 assistant 消息回填，不混入 dispatch 首包状态对齐或 task events 契约清理
- [x] 阅读 `chat-hardening` step-03 的轮询完成语义、step-04 的失败收口和当前 finalize 触发条件，确认问题集中在”完成事件必须出现在当前结果页”的假设
- [x] 检查现有 chat message 落地、task 完成判断和重复 finalize 防护边界，确认本 step 不需要额外拆分新的后台补偿前置 change
- [x] 进一步确认 `chat-hardening` 在本 step 只修复 polling 自恢复 finalize，不引入新的后台扫描器、定时任务或通用消息修复平台

## 2. finalize 恢复与消息回填

- [x] 调整 polling 完成判断与 finalize 触发逻辑，使 task 已完成但 assistant 消息尚未落地时仍能进入受控恢复路径
- [x] 保证 finalize / backfill 在重复轮询、恢复轮询和首次 finalize 失败后重试时保持幂等，不重复生成 assistant 消息

## 3. 轮询语义与日志收口

- [x] 明确”当前无新增事件””task 已完成但待补落消息””task 已完成且消息已落地”之间的受控边界，避免轮询语义再次混淆
- [x] 为 finalize 恢复失败补齐必要的结构化日志与错误上下文，避免问题只能依赖临时控制台日志排查

## 4. 验证与测试

- [x] 为 finalize 首次失败后的恢复、越过完成事件页后的消息补落、重复轮询幂等和正常完成主线补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `fix/chat-hardening-step-06-polling-finalization-recovery-and-backfill` squash merge 回 `series/chat-hardening`
- 说明：`series/chat-hardening -> dev` 不在本 change 内执行，该操作由人工负责

