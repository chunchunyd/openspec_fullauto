# 任务拆解：Chat Hardening Step 07 Task Events 契约回对齐

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/chat-hardening` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/chat-hardening` 切出 `fix/chat-hardening-step-07-task-events-contract-realignment` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/chat-hardening-step-07-task-events-contract-realignment` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 task events 契约、DTO 与 OpenAPI 导出对齐，不混入 dispatch 首包或 polling finalize 的行为修复
- [x] 阅读 `chat-hardening` step-02 到 step-06 的事件语义、当前 `chat.service.ts` / `chat.controller.ts` / `chat.dto.ts` 的返回结构和导出结果，确认真实返回应作为当前契约真相源
- [x] 检查现有 `packages/api_contracts` 导出链路、DTO 复用边界和代表性测试覆盖，确认本 step 不需要额外拆分新的共享契约前置 change
- [x] 进一步确认 `chat-hardening` 在本 step 只追平 task events 契约，不新增新的事件类型、前端 SDK 包装或推送协议

## 2. 契约与文档回对齐

- [x] 对齐 task events 的 DTO、Swagger 装饰或等价导出源，使其准确表达 `content` 结构、`progress` 字段和实际状态枚举
- [x] 明确 `PROCESSING`、`COMPLETED`、`FAILED`、`UNKNOWN` 等状态以及代表性事件载荷的正式文档语义，避免继续沿用旧的 `reply.*` 命名

## 3. 导出与回归保护

- [x] 更新 `packages/api_contracts/openapi/openapi.json` 或等价导出结果，确保生成契约与服务真实返回一致
- [x] 为 task events 契约、OpenAPI 导出和代表性响应样例补齐回归校验，防止 service / controller / DTO 再次漂移

## 4. 验证与测试

- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `fix/chat-hardening-step-07-task-events-contract-realignment` squash merge 回 `series/chat-hardening`
- 说明：`series/chat-hardening -> dev` 不在本 change 内执行，该操作由人工负责

