# 任务拆解：Admin Audit Part1 Step 05 用户读取门禁加固

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/admin-audit-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/admin-audit-part1` 切出 `fix/admin-audit-part1-step-05-user-read-guard-hardening` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/admin-audit-part1-step-05-user-read-guard-hardening` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 阅读 `admin-audit-part1-step-01-admin-identity-and-role-gate`、`admin-audit-part1-step-03-user-management-query-baseline` 与 `reports/api/admin-audit-part1/app-api-admin-audit-part1-review-v1.md`，确认本 step 只收口后台用户读取门禁

## 2. 用户读取门禁切换

- [ ] 2.1 将 `GET /admin/users` 与 `GET /admin/users/:userId` 切回 `AdminGuard` 主线，并显式声明最低读取角色
- [ ] 2.2 明确后台用户不存在、已禁用和权限不足时的受控拒绝语义，避免继续接受伪造 `x-admin-user-id`
- [ ] 2.3 如 `AdminInternalGuard` 仍被保留，明确它不再承担后台用户正式读取边界的权威校验职责

## 3. 测试与回归保护

- [ ] 3.1 对齐 `admin-users` 相关集成测试的 provider 装配，使其真实覆盖 `AdminGuard -> AdminIdentityService -> AdminIdentityRepository` 链路
- [ ] 3.2 补充后台用户不存在、已禁用和正常读取通过的回归测试
- [ ] 3.3 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 4. 验证与收口

- [ ] 4.1 执行 `admin-users` 相关 Jest 验收，确认读取接口的门禁与拒绝语义符合预期
- [ ] 4.2 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 4.3 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收；如果仍受 admin 范围外共享依赖阻塞，记录 blocker 并确认本 step 未新增新的类型回归
- [ ] 4.4 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/admin-audit-part1-step-05-user-read-guard-hardening` merge 回 `series/admin-audit-part1`，保留实现分支上的阶段性提交历史

- 说明：`series/admin-audit-part1 -> dev` 不在本 change 内执行，该操作由人工负责。

