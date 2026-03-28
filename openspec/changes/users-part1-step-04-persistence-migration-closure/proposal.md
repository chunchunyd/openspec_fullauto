# 变更提案：Users Part1 Step 04 持久化 migration 收口

## 为什么要做

上一轮对 `series/users-part1` 的验收表明，`prisma/schema.prisma` 已经承载了 self profile 字段与 `UserSettings` 宿主，但仓库还没有对应的正式 migration 历史。如果继续保持当前状态，新环境和 CI 只能依赖“直接拿当前 schema 建库”的隐式前提，无法通过已提交 migration 重建 `users-part1` 的真实持久化结构。

本批 change 继续沿用 `users-part1` 作为 series prefix，并把这一步限制在 persistence 收口，不同时混入请求校验加固或共享 OpenAPI 契约同步。

## 本次变更包含什么

- 为 `User.nickname`、`User.avatar`、`User.bio` 与 `UserSettings` 宿主补齐正式 Prisma migration 历史
- 校验当前 `prisma/schema.prisma` 与已提交 migration 历史不再漂移
- 确认新环境能够仅通过 migration 重建 `users-part1` 当前已交付的数据结构

## 本次变更不包含什么

- 新的资料字段、设置字段或额外 users 业务能力
- `users` 控制器请求校验与错误语义返工
- `packages/api_contracts/openapi/openapi.json` 导出同步

## 预期结果

1. `users-part1` 当前已进入 schema 的资料与设置结构拥有正式 migration 历史。
2. 新环境不需要依赖人工补表或直接读取 schema 文件，就能通过 migration 获得正确的数据结构。
3. 后续 `users-part1` 的接口加固和契约同步可以建立在稳定的数据库基线上继续推进。

## 影响范围

- `prisma/schema.prisma`
- `prisma/migrations/*`
- 必要时的 `prisma/README.md` 或等价说明
