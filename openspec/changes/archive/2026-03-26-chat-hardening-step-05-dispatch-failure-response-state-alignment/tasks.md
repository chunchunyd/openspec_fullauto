# 任务拆解：Chat Hardening Step 05 Dispatch 失败返回态一致性修复

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-05-dispatch-failure-response-state-alignment` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/chat-hardening-step-05-dispatch-failure-response-state-alignment` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 dispatch 失败后的即时响应状态，不混入 finalize 恢复或 task events 契约调整
- [x] 阅读 `chat-hardening` step-04 的失败状态修复结果、当前 `POST /chat/send` 返回组装逻辑和相关测试，确认旧内存态是响应断层的唯一收口目标
- [x] 检查现有 chat 失败信息映射、重试标记与 message/task DTO 复用边界，确认本 step 不需要额外拆分新的共享契约前置 change
- [x] 进一步确认 `chat-hardening` 在本 step 只处理发送首包与落库失败状态一致性，不混入 public chat、通用补偿平台或新的重试入口

## 2. 发送首包失败态对齐

- [x] 修正 dispatch bootstrap 失败后的发送结果组装逻辑，确保响应中的消息状态、任务状态与失败信息对齐最新持久化结果
- [x] 明确首包失败返回中的可重试语义和失败信息投影，避免客户端必须再次读取历史或事件接口才能识别失败

## 3. 回归保护

- [x] 为 dispatch bootstrap 失败时的首包状态、失败信息和可重试标识补齐回归测试
- [x] 确认成功发送、正常排队和失败分支之间的返回语义边界清晰，不因本 step 破坏既有成功主线

## 4. 验证与测试

- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `fix/chat-hardening-step-05-dispatch-failure-response-state-alignment` squash merge 回 `series/chat-hardening`
- 说明：`series/chat-hardening -> dev` 不在本 change 内执行，该操作由人工负责

