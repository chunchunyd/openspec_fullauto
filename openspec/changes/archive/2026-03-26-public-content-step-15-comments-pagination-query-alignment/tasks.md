# 任务拆解：Public Content Step 15 评论分页查询契约对齐

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `fix/public-content-step-15-comments-pagination-query-alignment` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/public-content-step-15-comments-pagination-query-alignment` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 comments list 的 HTTP 查询分页契约，不混入评论父帖子边界返工、行为信号测试补强或共享 OpenAPI 导出
- [x] 阅读 `reports/api/public-content/app-api-public-content-review-v2.md`、`public-content-step-13-public-interaction-boundary-hardening` 归档结果和当前 comments controller / dto，确认缺口只在查询参数解释链路

## 2. Comments 分页输入对齐

- [x] 为 comments list 的 `limit` 查询参数补齐显式数字转换，并保持现有最小值 / 最大值约束不变
- [x] 核对 controller、DTO 注释和接口说明，确认 comments list 的真实 HTTP 输入语义与当前文档一致

## 3. 回归测试

- [x] 为 comments list 增补代表性的 controller 或等价验证用例，覆盖 `limit=20` 可通过、`limit=0` 被拒绝、`limit=101` 被拒绝
- [x] 核对现有 comments 相关测试，避免继续只在 service 层以 number 形式绕过真实 HTTP 查询字符串场景

## 4. 验证与测试

- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 按 comments 相关链路执行 targeted jest 或等价验证，确认分页查询契约在真实输入形态下恢复为绿色
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `fix/public-content-step-15-comments-pagination-query-alignment` merge 回 `series/public-content`，保留实现分支上的阶段性提交历史
- 说明：`series/public-content -> dev` 不在本 change 内执行，该操作由人工负责
