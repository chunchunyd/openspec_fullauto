# 任务拆解：Admin Audit Part1 Step 04 用户状态治理动作

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/admin-audit-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/admin-audit-part1` 切出 `feat/admin-audit-part1-step-04-user-status-governance-actions` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/admin-audit-part1-step-04-user-status-governance-actions` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读 step-01 的角色门禁、step-02 的审计读取边界和 step-03 的用户查询结果，确认治理动作复用既有后台身份与审计主线
- [x] 检查现有后台鉴权链路、审计主存储与 `packages/api_contracts` 是否可复用，确认本 step 不需要额外拆分新的共享契约前置 change
- [x] 进一步确认 `admin-audit-part1` 在本 step 只落用户状态治理动作，不混入申诉流程、内容级联处置或自动化风控编排

## 2. 治理动作与状态流转

- [x] 定义用户封禁与解封的最小状态流转、原因码或备注和幂等语义
- [x] 建立受角色约束的治理接口，保证高风险动作不能被低权限角色执行

## 3. 审计留痕与影响边界

- [x] 将治理动作写入权威审计记录，确保后台后续可追溯操作人、目标对象和结果
- [x] 明确治理结果对登录或关键行为的最小影响边界，并避免越权修改其他业务主状态
- [x] 为治理动作成功、拒绝和审计写入异常补齐必要的结构化日志与错误上下文

## 4. 验证与测试

- [x] 为封禁成功、解封成功、重复操作幂等、低权限拒绝和审计记录生成补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题

  状态：已完成。修复了 admin 模块的 ESLint 错误（prettier 格式化、未使用导入、unbound-method 等）。

- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误

  状态：已完成。修复了 admin 模块的 TypeScript 错误（Prisma InputJsonValue 类型、import type 导入、AdminUserNotFoundResponse 接口不匹配等）。

- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净

  状态：已完成。提交 `97fcd5d admin-audit-part1-step-04-user-status-governance-actions: 建立用户状态治理动作基线`。

- [x] 自动化将 `feat/admin-audit-part1-step-04-user-status-governance-actions` squash merge 回 `series/admin-audit-part1`

  说明：此任务由 wrapper 自动管理，父脚本会处理同步。

- 说明：`series/admin-audit-part1 -> dev` 不在本 change 内执行，该操作由人工负责
