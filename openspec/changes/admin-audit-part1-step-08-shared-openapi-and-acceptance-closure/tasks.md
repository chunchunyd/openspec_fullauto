# 任务拆解：Admin Audit Part1 Step 08 共享 OpenAPI 与验收收口

## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/admin-audit-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/admin-audit-part1` 切出 `chore/admin-audit-part1-step-08-shared-openapi-and-acceptance-closure` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `chore/admin-audit-part1-step-08-shared-openapi-and-acceptance-closure` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 阅读 `admin-audit-part1-step-05-user-read-guard-hardening`、`admin-audit-part1-step-06-user-governance-state-machine-hardening`、`admin-audit-part1-step-07-audit-query-boundary-hardening` 与 `reports/api/admin-audit-part1/app-api-admin-audit-part1-review-v1.md`，确认本 step 只处理契约与验收收口

## 2. 契约对齐

- [ ] 2.1 对齐 ban / unban 等后台治理动作的实际 HTTP 状态码与 Swagger 注解，避免继续出现 `201` / `200` 漂移
- [ ] 2.2 审阅 `admin/users`、`admin/audit/logs` 与本系列受影响接口的 Swagger 注解，确保共享 OpenAPI 能表达当前已交付的成功、拒绝和校验失败语义
- [ ] 2.3 如共享契约消费入口或导出说明发生实质变化，补充必要的 README 或相关文档说明

## 3. 测试收口

- [ ] 3.1 修复 `admin-users` 与 `admin-agents` 集成测试的 guard 依赖装配，使其按真实 `AdminGuard` 依赖图运行
- [ ] 3.2 重新执行 admin 相关 targeted Jest 验收，确认 users / agents / audit / governance 套件都能真实通过
- [ ] 3.3 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 4. 共享 OpenAPI 导出与最终验收

- [ ] 4.1 执行 `pnpm openapi-export` 或等价导出流程，刷新 `packages/api_contracts/openapi/openapi.json`
- [ ] 4.2 核对导出产物已覆盖 `admin-audit-part1` 本轮交付接口的当前契约语义
- [ ] 4.3 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 4.4 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收；如果仍受 admin 范围外共享依赖阻塞，记录 blocker 并确认本 step 未新增新的类型回归

## 5. 合并与收口

- [ ] 5.1 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `chore/admin-audit-part1-step-08-shared-openapi-and-acceptance-closure` merge 回 `series/admin-audit-part1`，保留实现分支上的阶段性提交历史

- 说明：`series/admin-audit-part1 -> dev` 不在本 change 内执行，该操作由人工负责。

