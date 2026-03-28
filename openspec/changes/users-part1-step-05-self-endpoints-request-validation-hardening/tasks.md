# 任务拆解：Users Part1 Step 05 自我资料与设置接口请求校验加固

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/users-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/users-part1` 切出 `fix/users-part1-step-05-self-endpoints-request-validation-hardening` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/users-part1-step-05-self-endpoints-request-validation-hardening` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 阅读 `users-part1-step-02-self-profile-update-boundary`、`users-part1-step-03-preferences-and-notification-settings-baseline` 与 `openspec/specs/users/spec.md`，确认本 step 只处理写入入口的请求校验加固

## 2. 请求校验边界

- [ ] 2.1 在 `UsersController` 上接入与现有受控 API 一致的 `ValidationPipe` 策略，至少包含 `whitelist`、`forbidNonWhitelisted` 与 `transform`
- [ ] 2.2 为 self settings DTO 补齐 `class-validator` / `class-transformer` 约束，明确语言枚举、布尔类型与非白名单字段的请求校验语义
- [ ] 2.3 梳理 self profile / self settings 写入路径中的 400 校验错误与业务错误边界，避免无效输入继续流入 service / repository

## 3. 测试与注释

- [ ] 3.1 为 `/users/me` 与 `/users/me/settings` 补充 controller 或等价集成测试，覆盖未登录、非白名单字段、错误类型、非法取值与局部更新主线
- [ ] 3.2 如果本 step 新增或修改自动化测试文件，在测试文件头注释中写明完整执行命令
- [ ] 3.3 补充必要的控制器注释或模块说明，解释 users 写入边界与 auth-owned 字段隔离语义

## 4. 验证与收口

- [ ] 4.1 执行 users 相关自动化测试与当前 change 对应的 API 验证，确认无效输入被稳定拒绝
- [ ] 4.2 按 `docs/eslint-style-notes.md` 的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 4.3 按 `docs/tsc-fix-summary.md` 的当前约定执行 TypeScript 验收；如果仍受 users 范围外共享依赖阻塞，记录 blocker 并确认本 step 未新增新的 users 模块类型回归
- [ ] 4.4 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/users-part1-step-05-self-endpoints-request-validation-hardening` merge 回 `series/users-part1`，保留实现分支上的阶段性提交历史

- 说明：共享 OpenAPI 导出与契约同步由 `users-part1-step-06-shared-openapi-contract-and-acceptance-closure` 收口。
- 说明：`series/users-part1 -> dev` 不在本 change 内执行，该操作由人工负责。
