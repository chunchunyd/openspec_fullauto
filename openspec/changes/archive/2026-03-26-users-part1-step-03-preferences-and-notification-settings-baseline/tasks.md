# 任务拆解：Users Part1 Step 03 偏好与通知设置基线

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/users-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/users-part1` 切出 `feat/users-part1-step-03-preferences-and-notification-settings-baseline` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/users-part1-step-03-preferences-and-notification-settings-baseline` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读 `users-part1-step-01-profile-data-model-and-self-read-baseline`、`users-part1-step-02-self-profile-update-boundary` 与现有 `openspec/specs/analytics/spec.md`，确认当前设置只服务用户侧自我配置
- [x] 检查现有 `packages/api_contracts` 与 `openapi-export` 导出链路是否可复用，确认本 step 不需要额外拆分新的共享契约前置 change
- [x] 进一步确认 `users-part1` 在本 step 只落最小偏好与通知开关宿主，不混入推送投递、推荐策略执行或复杂隐私矩阵

## 2. 设置模型与默认值

- [x] 为偏好与通知设置补齐最小持久化锚点、默认值语义和前向兼容字段组织
- [x] 明确读取时默认回填与局部更新时的 merge 语义

## 3. 自我配置边界

- [x] 建立自我设置读取与更新接口，返回当前有效的设置结果
- [x] 限定当前 step 只暴露首期必要开关，不提前承诺复杂策略参数

## 4. 验证与测试

- [x] 为默认设置读取、局部更新、非法键拒绝和未登录拒绝补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `feat/users-part1-step-03-preferences-and-notification-settings-baseline` squash merge 回 `series/users-part1`
- 说明：`series/users-part1 -> dev` 不在本 change 内执行，该操作由人工负责
