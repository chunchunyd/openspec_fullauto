# 任务拆解：Chat Hardening Step 04 Dispatch 失败状态与重试闭环修复

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-04-dispatch-failure-state-and-retry-closure` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/chat/spec.md`、当前失败状态读取逻辑与重试门禁逻辑
- [x] 确认当前 step 只收口 dispatch 失败与重试闭环，不扩展到 public chat 或通用补偿平台

## 2. 失败状态一致性修复

- [x] 修正 dispatch bootstrap 失败时的消息状态、任务状态和失败信息写入，避免出现"任务失败但消息未失败"的断层
- [x] 明确历史消息读取中失败信息与可重试标识的映射规则，使其与真实失败主线保持一致

## 3. 重试门禁与重试主线收口

- [x] 调整重试门禁，使其基于一致的失败状态判断而不是依赖单一旧状态假设
- [x] 确认重试后新的任务关联、原始失败消息与重复点击幂等控制之间的边界清晰可追踪

## 4. 验证与测试

- [x] 为 dispatch 失败后的消息状态、历史读取失败信息、可重试判定和成功重试主线补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `fix/chat-hardening-step-04-dispatch-failure-state-and-retry-closure` squash merge 回 `series/chat-hardening`
- `series/chat-hardening -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

