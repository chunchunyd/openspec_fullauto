# 任务拆解：Admin Audit Part1 Step 01 后台身份与角色门禁

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/admin-audit-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/admin-audit-part1` 切出 `feat/admin-audit-part1-step-01-admin-identity-and-role-gate` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/admin-audit-part1-step-01-admin-identity-and-role-gate` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读 `openspec/specs/admin/spec.md`、`openspec/specs/auth/spec.md`、当前 `apps/api/src/modules/admin/*` 与已存在的鉴权链路，确认后台身份不等同于普通消费侧权限
- [x] 检查现有后台鉴权链路、`packages/api_contracts` 与请求上下文封装是否可复用，确认本 step 不需要额外拆分新的共享契约前置 change
- [x] 进一步确认 `admin-audit-part1` 在本 step 只建立后台身份与角色门禁，不混入用户管理、审计读取或内容治理主线

## 2. 身份来源与角色模型

- [x] 明确后台身份来源、角色分级和与普通用户登录态的关系，避免直接把消费侧权限当后台权限
- [x] 为后台接口补齐统一 guard、decorator、上下文提取或等价门禁基线

## 3. 最小验证入口

- [x] 提供最小后台身份探测入口或等价受保护接口，用于验证后台登录态与角色门禁
- [x] 明确普通用户拒绝、低权限拒绝和高权限通过语义

## 4. 验证与测试

- [x] 为后台用户通过、普通用户拒绝、低权限拒绝和上下文缺失拒绝补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `feat/admin-audit-part1-step-01-admin-identity-and-role-gate` squash merge 回 `series/admin-audit-part1`
- 说明：`series/admin-audit-part1 -> dev` 不在本 change 内执行，该操作由人工负责
