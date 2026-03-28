# 任务拆解：Users Part1 Step 01 资料模型与自我读取基线

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/users-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/users-part1` 切出 `feat/users-part1-step-01-profile-data-model-and-self-read-baseline` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/users-part1-step-01-profile-data-model-and-self-read-baseline` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读现有 `openspec/specs/auth/spec.md`、`openspec/specs/admin/spec.md`、`prisma/schema.prisma` 与当前 auth 自我态返回边界，确认 `users` 不重复承载认证主状态
- [x] 检查现有 `packages/api_contracts` 与 `openapi-export` 导出链路是否可复用，确认本 step 不需要额外拆分新的共享契约前置 change
- [x] 进一步确认 `users-part1` 在本 step 只建立 self profile 和最小设置宿主，不混入后台治理、账户注销、黑名单或推荐画像

## 2. 数据模型与模块边界

- [x] 为用户资料补齐最小持久化锚点、可空字段和默认值策略，明确 `auth` 字段与 `users` 字段的归属
- [x] 初始化 `apps/api/src/modules/users/*` 的最小 service/controller/module 边界，避免继续把资料读取逻辑塞回 `auth`

## 3. 自我读取契约

- [x] 建立 `GET /users/me` 或等价自我读取接口，返回受控的基础资料结果和缺省字段
- [x] 明确未登录拒绝、资料缺省值和尚未补全资料时的返回语义

## 4. 验证与测试

- [x] 为自我读取成功、未登录拒绝、资料字段缺省回填和 auth-owned 字段不被错误暴露补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `feat/users-part1-step-01-profile-data-model-and-self-read-baseline` squash merge 回 `series/users-part1`
- 说明：`series/users-part1 -> dev` 不在本 change 内执行，该操作由人工负责
