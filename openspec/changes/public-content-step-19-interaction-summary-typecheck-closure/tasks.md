# 任务拆解：Public Content Step 19 互动摘要类型校验收口

## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/public-content` 切出 `fix/public-content-step-19-interaction-summary-typecheck-closure` 实现分支，并将当前 worktree 绑定到该分支
- 说明：在进入实现分支前不进行任何实现性编辑是执行原则，非可勾选任务
- 说明：续跑或接手已有 worktree 时的 staged / unstaged / untracked 现场检查是执行原则，非可勾选任务
- [ ] 确认当前 step 只收口互动摘要测试夹具与类型校验链，不混入新的互动字段、统计口径或聚合策略
- [ ] 阅读 `reports/api/public-content/app-api-public-content-review-v3.md`、`apps/api/src/modules/interactions/interaction-summary.service.ts` 与 `apps/api/src/modules/interactions/__tests__/interaction-summary.service.spec.ts`，确认 drift 集中在 Prisma delegate mock 的类型表达

## 2. 互动摘要测试与类型收口

- [ ] 把 `interaction-summary.service.spec.ts` 中的 Prisma / repository test double 改成显式且类型兼容的 mock 结构，不再把原始 Prisma `groupBy` 方法直接当成 Jest mock 使用
- [ ] 核对帖子详情、批量摘要和 feed 卡片摘要当前复用的最小投影语义，确认本 step 不改变既有运行时行为

## 3. 验证与验收

- [ ] 执行 `pnpm --dir apps/api exec jest src/modules/interactions/__tests__/interaction-summary.service.spec.ts --runInBand`，确认互动摘要代表性测试继续通过
- [ ] 执行 `pnpm --dir apps/api exec jest src/modules/interactions --runInBand`，确认 interactions 主线未被 summary 测试夹具调整带偏
- [ ] 按 `docs/tsc-fix-summary.md` 的当前约定执行 `pnpm --dir apps/api exec tsc -p tsconfig.json --noEmit`，并明确区分本 step 清理后的剩余基线问题

## 4. 文档与合并

- [ ] 按 `docs/eslint-style-notes.md` 的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令
- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/public-content-step-19-interaction-summary-typecheck-closure` merge 回 `series/public-content`，保留实现分支上的阶段性提交历史
- 说明：`series/public-content -> dev` 不在本 change 内执行，该操作由人工负责
