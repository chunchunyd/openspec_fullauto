# 变更提案：Admin Audit Part1 Step 05 用户读取门禁加固

## 为什么要做

`admin-audit-part1` 的验收表明，当前 `GET /admin/users` 与 `GET /admin/users/:userId` 仍挂在只校验 header 存在性的 `AdminInternalGuard` 上，没有真正复用 step-01 建立的后台身份验证与角色门禁基线。

这意味着一旦 `x-admin-api-key` 泄露，请求方可以伪造任意非空 `x-admin-user-id` 读取后台用户列表和用户详情，和 step-01 “独立后台身份上下文与角色门禁保护后台入口”的承诺不一致。

本 step 继续沿用 `admin-audit-part1` 作为 series prefix，只收口后台用户读取边界的身份校验与角色语义，不混入用户状态治理状态机返工、审计查询契约硬化或共享 OpenAPI 导出收口。

## 本次变更包含什么

- 将后台用户列表与用户详情读取边界切回已验证的 `AdminGuard` 主线
- 为后台用户读取接口显式声明最低角色要求，避免“默认任何 header 通过”的隐式语义
- 对齐 `admin-users` 相关集成测试，覆盖后台用户不存在、已禁用和正常读取等关键场景

## 本次变更不包含什么

- 用户封禁 / 解封状态机修正
- 审计中心查询时间范围与排序参数硬化
- `admin-audit-part1` 的共享 OpenAPI 导出与最终验收收口

## 预期结果

1. `GET /admin/users` 与 `GET /admin/users/:userId` 必须依赖已验证的后台身份上下文，而不是仅依赖 header 形式正确。
2. 后台用户不存在、已禁用或不满足最低角色要求时，读取接口会返回受控拒绝结果。
3. `admin-users` 读取链路重新与 step-01 的后台门禁基线对齐。

## 影响范围

- `apps/api/src/modules/admin/admin-users.controller.ts`
- `apps/api/src/modules/admin/admin.guard.ts`
- 必要时的 `apps/api/src/modules/admin/admin-internal.guard.ts`
- `apps/api/src/modules/admin/__tests__/admin-users.controller.integration.spec.ts`

