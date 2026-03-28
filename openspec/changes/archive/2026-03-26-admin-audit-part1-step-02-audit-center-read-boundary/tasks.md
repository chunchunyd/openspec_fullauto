# 任务拆解：Admin Audit Part1 Step 02 审计中心读取边界

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/admin-audit-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/admin-audit-part1` 切出 `feat/admin-audit-part1-step-02-audit-center-read-boundary` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/admin-audit-part1-step-02-audit-center-read-boundary` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读当前 `apps/api/src/modules/audit/*`、`openspec/specs/audit-log/spec.md` 与 step-01 的后台门禁基线，确认复用既有权威审计记录
- [x] 检查现有审计主存储、后台鉴权链路与 `packages/api_contracts` 是否可复用，确认本 step 不新增 analytics 派生 owner 或新的共享契约前置 change
- [x] 进一步确认 `admin-audit-part1` 的本 step 只补后台审计中心读取边界，不混入治理动作写入改造或异常告警系统

## 2. 读取模型与字段口径

- [x] 为审计中心定义最小查询条件、分页排序和结果字段裁剪
- [x] 明确 actor、target、action、result、time 等上下文字段的读取口径与敏感字段处理

## 3. 后台读取边界

- [x] 建立后台审计读取接口或等价 service 边界，复用现有审计记录主存储
- [x] 保证无权限访问、越权条件和空结果场景的受控返回

## 4. 验证与测试

- [x] 为审计读取成功、筛选分页、越权拒绝和敏感字段受控返回补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `feat/admin-audit-part1-step-02-audit-center-read-boundary` squash merge 回 `series/admin-audit-part1`
- 说明：`series/admin-audit-part1 -> dev` 不在本 change 内执行，该操作由人工负责
