# 任务拆解: Chat Hardening Step 09 Task Events 受控错误契约补齐

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪(若不存在则从最新 `dev` 创建)
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-09-task-events-controlled-error-contract-closure` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/chat-hardening-step-09-task-events-controlled-error-contract-closure` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 task-events 的受控错误 / 未就绪 HTTP 契约，不混入 finalize 原子收口或 send / retry 验收链修复
- [x] 阅读 `chat-hardening` step-02 与 step-07 的结果、当前 `chat.service.ts` / `chat.controller.ts` / `chat.dto.ts` / OpenAPI 导出，确认丢失点集中在 controller 与共享契约层

## 2. 受控错误契约

- [x] 为 `GET /chat/tasks/:taskId/events` 明确 not-linked、runtime-unavailable 与 normal-empty 的对外契约表达，保持现有 polling 主线可继续消费
- [x] 对齐 service、controller 和 DTO 的字段传递，避免 `result.error` 在 HTTP 层被静默吞掉

## 3. OpenAPI 与文档

- [x] 更新 Swagger / OpenAPI 导出源，并执行 `openapi-export`，确保 `packages/api_contracts/openapi/openapi.json` 能表达 task-events 的受控错误字段
- [x] 如 `apps/api/README.md` 已描述 task-events 使用方式，补充"无新增事件""runtime 未映射""runtime 暂不可读"三类结果的差异说明

## 4. 验证与测试

- [x] 为 runtimeTaskId 缺失、runtime 暂不可读和正常空页轮询三类场景补充 controller / contract 级回归测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `fix/chat-hardening-step-09-task-events-controlled-error-contract-closure` merge 回 `series/chat-hardening`，保留实现分支上的阶段性提交历史
- 说明：`series/chat-hardening -> dev` 不在本 change 内执行，该操作由人工负责
