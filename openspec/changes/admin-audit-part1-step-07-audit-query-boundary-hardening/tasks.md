# 任务拆解：Admin Audit Part1 Step 07 审计查询边界加固

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/admin-audit-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/admin-audit-part1` 切出 `fix/admin-audit-part1-step-07-audit-query-boundary-hardening` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/admin-audit-part1-step-07-audit-query-boundary-hardening` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 阅读 `admin-audit-part1-step-02-audit-center-read-boundary` 与 `reports/api/admin-audit-part1/app-api-admin-audit-part1-review-v1.md`，确认本 step 只收口后台审计查询参数与时间区间边界

## 2. 查询参数硬化

- [ ] 2.1 修正后台审计查询中 `startTime` 与 `endTime` 的组合逻辑，确保时间区间条件能同时生效
- [ ] 2.2 为 `sortBy` / `sortOrder` 建立显式白名单与仓储层字段映射，避免非法参数继续落到动态 `orderBy`
- [ ] 2.3 确认非法排序参数、非法页码与非法筛选参数都保持受控拒绝语义

## 3. 测试与回归保护

- [ ] 3.1 补充同时传入 `startTime` 与 `endTime` 的回归测试，证明时间区间真实生效
- [ ] 3.2 补充非法 `sortBy` / `sortOrder` 被 400 拒绝的回归测试
- [ ] 3.3 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 4. 验证与收口

- [ ] 4.1 执行 `admin-audit` 相关 Jest 验收，确认查询组合、非法参数和现有成功路径都符合预期
- [ ] 4.2 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 4.3 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收；如果仍受 admin 范围外共享依赖阻塞，记录 blocker 并确认本 step 未新增新的类型回归
- [ ] 4.4 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/admin-audit-part1-step-07-audit-query-boundary-hardening` merge 回 `series/admin-audit-part1`，保留实现分支上的阶段性提交历史

- 说明：`series/admin-audit-part1 -> dev` 不在本 change 内执行，该操作由人工负责。

