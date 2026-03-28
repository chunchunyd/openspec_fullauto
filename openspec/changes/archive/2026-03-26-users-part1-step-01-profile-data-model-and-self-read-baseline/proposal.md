# 变更提案：Users Part1 Step 01 资料模型与自我读取基线

## 为什么要做

当前仓库中的 `users` 模块尚未开工，用户资料边界仍散落在 `auth` 的账号最小状态与未来业务字段预期之间。作为 `users-part1` 的起点，本 step 需要先把“用户自己的资料主数据 + 自我读取入口”稳定下来，避免后续资料编辑、偏好设置继续直接堆回 `auth`。

本批 change 使用 `users-part1` 作为 series prefix，且 `part1` 只覆盖 self profile 与最小设置宿主。当前 step 复用现有 `auth` 边界与 `packages/api_contracts` 导出链路，不额外引入新的 `libs/` 共享层前置 change。

## 本次变更包含什么

- 为 `users-part1` 建立最小用户资料主数据锚点，明确哪些字段归 `users`，哪些字段仍归 `auth`
- 提供 `GET /users/me` 或等价的自我资料读取边界
- 返回已登录用户当前可展示的基础资料与可空默认值

## 本次变更不包含什么

- 自我资料更新
- 偏好、通知与隐私设置写入
- 后台用户管理、封禁、注销或账户删除

## 预期结果

1. `users` 模块拥有独立于 `auth` 的资料主数据起点。
2. 已登录用户可以通过统一入口读取自己的基础资料。
3. 后续 step 可以在不回滚边界的前提下继续补资料编辑和设置能力。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/users/*`
- `apps/api/src/modules/auth/*`
- `packages/api_contracts/openapi/openapi.json`
