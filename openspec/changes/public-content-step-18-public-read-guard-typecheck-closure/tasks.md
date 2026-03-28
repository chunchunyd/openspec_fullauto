# 任务拆解：Public Content Step 18 公开读取守卫类型校验收口

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `fix/public-content-step-18-public-read-guard-typecheck-closure` 实现分支，并将当前 worktree 绑定到该分支
- 说明：在进入实现分支前不进行任何实现性编辑是执行原则，非可勾选任务
- 说明：续跑或接手已有 worktree 时的 staged / unstaged / untracked 现场检查是执行原则，非可勾选任务
- [ ] 确认当前 step 只收口公开读取守卫测试与 public read 验收链，不混入新的 feed/detail 运行时语义或 auth 能力扩张
- [ ] 阅读 `reports/api/public-content/app-api-public-content-review-v3.md`、`apps/api/src/common/guards/optional-auth.guard.ts`、`apps/api/src/common/guards/__tests__/optional-auth.guard.spec.ts` 与 public feed/detail 当前控制器，确认 drift 集中在 guard test double 的类型断言

## 2. 守卫测试与类型收口

- [ ] 把 `OptionalAuthGuard` 测试中的 ExecutionContext helper 改成最小但类型兼容的 test double，不再通过整体 `never` 断言压掉 `switchToHttp()` 等接口类型
- [ ] 核对公开首页 feed 与公开帖子详情当前复用的可选认证读取主线，确认本 step 不改变匿名可读与登录态增强的既有运行时行为

## 3. 验证与验收

- [ ] 执行 `pnpm --dir apps/api exec jest src/common/guards/__tests__/optional-auth.guard.spec.ts --runInBand`，确认 `OptionalAuthGuard` 代表性路径继续通过
- [ ] 执行 `pnpm --dir apps/api exec jest src/modules/feed src/modules/content --runInBand`，确认 public read 主线未被 guard test 调整带偏
- [ ] 按 `docs/tsc-fix-summary.md` 的当前约定执行 `pnpm --dir apps/api exec tsc -p tsconfig.json --noEmit`，并明确区分本 step 清理后的剩余基线问题

## 4. 文档与合并

- [ ] 按 `docs/eslint-style-notes.md` 的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令
- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/public-content-step-18-public-read-guard-typecheck-closure` merge 回 `series/public-content`，保留实现分支上的阶段性提交历史
- 说明：`series/public-content -> dev` 不在本 change 内执行，该操作由人工负责
