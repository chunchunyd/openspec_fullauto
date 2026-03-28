# 变更提案：Users Part1 Step 05 自我资料与设置接口请求校验加固

## 为什么要做

上一轮对 `series/users-part1` 的验收表明，当前 `users` 控制器尚未接入与仓库其他受控接口一致的请求校验策略，`settings` DTO 也缺少真实的 `class-validator` 约束。这会导致 self profile 与 self settings 写入入口对非白名单字段、错误类型和未受支持取值的拒绝语义停留在注释和 service 假设里，而没有真正落在 API 边界。

本批 change 继续沿用 `users-part1` 作为 series prefix，并把这一步限制在 users 自我资料与设置接口的请求校验加固，不同时混入数据库 migration 收口或共享 OpenAPI 导出同步。

## 本次变更包含什么

- 在 `UsersController` 上补齐与现有受控 API 一致的 `ValidationPipe` 请求校验边界
- 为 self settings 请求 DTO 补齐真实的 `class-validator` / `class-transformer` 约束，并收紧 self profile / self settings 写入的非法输入语义
- 为 `/users/me` 与 `/users/me/settings` 补充 controller 或等价集成测试，覆盖未登录、非白名单字段、错误类型与非法受控取值

## 本次变更不包含什么

- 新的资料字段、设置字段或额外 users 业务能力
- `prisma/schema.prisma` 和 migration 历史回补
- `packages/api_contracts/openapi/openapi.json` 的共享契约导出同步

## 预期结果

1. `/users/me` 与 `/users/me/settings` 写入入口能够在进入持久化前拒绝非白名单字段、错误类型和未受支持的受控取值。
2. auth-owned 字段不会再以“静默吞掉后继续成功”的方式穿过 users 写入边界。
3. 后续共享 OpenAPI 导出可以建立在稳定的请求校验与错误语义之上继续收口。

## 影响范围

- `apps/api/src/modules/users/*`
- 必要时的 `apps/api/src/common/*` 受控请求校验复用入口
- `apps/api` 中与 users 自我接口相关的自动化测试
