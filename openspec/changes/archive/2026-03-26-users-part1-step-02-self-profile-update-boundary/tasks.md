# 任务拆解：Users Part1 Step 02 自我资料更新边界

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/users-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/users-part1` 切出 `feat/users-part1-step-02-self-profile-update-boundary` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/users-part1-step-02-self-profile-update-boundary` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读 `users-part1-step-01-profile-data-model-and-self-read-baseline` 的资料读取结果与当前 `auth` 登录态返回字段，确认可编辑字段白名单
- [x] 检查现有 `packages/api_contracts` 与 `openapi-export` 导出链路是否可复用，确认本 step 不需要额外拆分新的共享契约前置 change
- [x] 进一步确认本 step 只处理用户自我资料写入，不混入通知设置、后台治理或资源上传链路

## 2. 写入边界与字段校验

- [x] 建立 `PATCH /users/me` 或等价写入接口，限定昵称、简介、展示资料等可编辑字段
- [x] 为字段格式、长度、空值回退和不可编辑字段写入拒绝补齐校验

## 3. 读取一致性

- [x] 复用或同步 step-01 的读取结果，确保资料更新后自我读取立即返回最新受控结果
- [x] 明确部分字段更新、空值清除和未变更提交的受控语义

## 4. 验证与测试

- [x] 为资料更新成功、部分字段更新、非法字段拒绝、auth-owned 字段拒绝写入补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `feat/users-part1-step-02-self-profile-update-boundary` squash merge 回 `series/users-part1`
- 说明：`series/users-part1 -> dev` 不在本 change 内执行，该操作由人工负责
