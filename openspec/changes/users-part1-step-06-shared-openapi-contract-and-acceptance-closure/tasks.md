# 任务拆解：Users Part1 Step 06 共享 OpenAPI 契约与验收收口

## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/users-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/users-part1` 切出 `chore/users-part1-step-06-shared-openapi-contract-and-acceptance-closure` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `chore/users-part1-step-06-shared-openapi-contract-and-acceptance-closure` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 阅读 `users-part1-step-04-persistence-migration-closure`、`users-part1-step-05-self-endpoints-request-validation-hardening` 与 `openspec/specs/api-contracts/spec.md`，确认本 step 只处理共享契约与验收收口

## 2. 契约真相源与导出前检查

- [ ] 2.1 审阅 `UsersController` 与相关 DTO 的 Swagger 注解，确保 `/users/me` 与 `/users/me/settings` 的成功、未认证、业务错误和校验失败语义都有正式导出入口
- [ ] 2.2 如导出结果缺少代表性响应结构，补齐必要的 `ApiResponse`、`ApiBadRequestResponse`、`ApiUnauthorizedResponse` 或等价注解，而不是手工编辑共享产物

## 3. 共享 OpenAPI 导出

- [ ] 3.1 执行 `pnpm openapi-export` 或等价导出流程，更新 `packages/api_contracts/openapi/openapi.json`
- [ ] 3.2 核对导出产物已包含 `/users/me`、`/users/me/settings` 及代表性的成功、未认证和校验失败结构
- [ ] 3.3 如导出链路或消费入口发生实质变化，补充必要的 README 或相关文档说明

## 4. 验收与收口

- [ ] 4.1 执行 users-part1 相关验收命令，至少覆盖 users 写路径测试、共享契约导出检查与必要的手动 spot check
- [ ] 4.2 按 `docs/eslint-style-notes.md` 的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 4.3 按 `docs/tsc-fix-summary.md` 的当前约定执行 TypeScript 验收；如果仍受 users 范围外共享依赖阻塞，记录 blocker 并确认本 step 未新增新的类型回归
- [ ] 4.4 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `chore/users-part1-step-06-shared-openapi-contract-and-acceptance-closure` merge 回 `series/users-part1`，保留实现分支上的阶段性提交历史

- 说明：`series/users-part1 -> dev` 不在本 change 内执行，该操作由人工负责。
