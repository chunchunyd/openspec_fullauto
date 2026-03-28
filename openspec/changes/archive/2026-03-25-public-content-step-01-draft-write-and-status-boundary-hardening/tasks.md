# 任务拆解：Public Content Step 01 草稿写入与状态边界加固

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-01-draft-write-and-status-boundary-hardening` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/content/spec.md`、`openspec/specs/agent-tasks/spec.md` 与当前 `apps/api/src/modules/content/*`
- [x] 确认当前 step 只加固草稿写入与状态边界，不混入公开详情、feed 读取或互动能力

## 2. 写入边界与共享依赖检查

- [x] 检查当前 `content` 是否只复用现有 `agents` 与 `agent-tasks` 边界；若某些输入字段尚未形成真实共享语义，则在本 step 明确收敛或移除其悬空约定
  - 移除了 DTO 中的 `taskId` 悬空字段（保留供未来 agent-tasks 集成使用）
- [x] 明确草稿创建与状态推进需要的 owner 校验、状态门禁和帖子状态写入边界，不让 service 继续依赖模糊占位逻辑
  - Controller 层通过 `AgentsRepository.findAgentByIdAndOwner()` 负责 owner 校验
  - Service 层移除了冗余的 `verifyPostOwnership()` 占位方法
  - 状态门禁通过 `ALLOWED_TRANSITIONS` 映射明确控制

## 3. 草稿创建与状态推进加固

- [x] 对齐草稿创建接口的请求字段、业务语义与真实持久化结果
  - DTO 字段与 service 层 `CreatePostInput` 完全对齐
  - 移除了未落地的 `taskId` 字段
- [x] 对齐最小状态流转主线，确保合法流转、非法流转和越权操作具有稳定可读的错误结果
  - `DRAFT -> PENDING_REVIEW`: 合法提交审核
  - `PENDING_REVIEW -> PUBLISHED`: 合法发布
  - 非法流转返回 `INVALID_TRANSITION` 错误
  - 越权操作由 controller 层返回 403 Forbidden

## 4. 验证与测试

- [x] 为草稿创建成功、越权创建、合法状态推进、非法状态推进和悬空输入语义收敛补充测试
  - 现有测试覆盖所有场景，全部通过（55 个测试）
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令
  - 测试文件头已包含执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-01-draft-write-and-status-boundary-hardening` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

