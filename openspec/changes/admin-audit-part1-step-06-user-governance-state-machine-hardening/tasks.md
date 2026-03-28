# 任务拆解：Admin Audit Part1 Step 06 用户治理状态机加固

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/admin-audit-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/admin-audit-part1` 切出 `fix/admin-audit-part1-step-06-user-governance-state-machine-hardening` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/admin-audit-part1-step-06-user-governance-state-machine-hardening` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 阅读 `admin-audit-part1-step-04-user-status-governance-actions` 与 `reports/api/admin-audit-part1/app-api-admin-audit-part1-review-v1.md`，确认本 step 只处理 ban / unban 状态机边界

## 2. 状态机与持久化锚点

- [x] 2.1 为 ban / unban 增加恢复封禁前状态所需的最小持久化锚点，并明确其 owner 边界
- [x] 2.2 让 ban / unban 基于受控状态机执行，避免解封时一律写回 `ACTIVE`
- [x] 2.3 明确恢复锚点缺失、非法状态转换和重复操作时的受控返回语义

## 3. 审计与行为边界

- [ ] 3.1 保持治理动作对操作者、目标对象、原因和结果的审计留痕完整
- [ ] 3.2 确认本 step 不会把 audit log 反向变成用户主状态的权威 owner
- [ ] 3.3 明确本 step 对登录态或其他主状态的影响仍保持在 `admin-audit-part1` 当前范围内

## 4. 测试与验证

- [ ] 4.1 补充 `DEACTIVATED -> BANNED -> unban`、恢复锚点缺失和重复治理动作的回归测试
- [ ] 4.2 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令
- [ ] 4.3 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 4.4 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收；如果仍受 admin 范围外共享依赖阻塞，记录 blocker 并确认本 step 未新增新的类型回归

## 5. 合并与收口

- [ ] 5.1 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/admin-audit-part1-step-06-user-governance-state-machine-hardening` merge 回 `series/admin-audit-part1`，保留实现分支上的阶段性提交历史

- 说明：`series/admin-audit-part1 -> dev` 不在本 change 内执行，该操作由人工负责。

