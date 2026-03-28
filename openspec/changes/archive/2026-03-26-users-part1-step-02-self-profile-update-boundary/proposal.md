# 变更提案：Users Part1 Step 02 自我资料更新边界

## 为什么要做

在 `users-part1` 已建立自我资料读取基线之后，下一步需要补齐受控的自我资料更新边界，让用户资料不再只能读不能改，同时把可编辑资料与 `auth` 持有的登录身份字段彻底分层。

本批 change 继续沿用 `users-part1` 作为 series prefix，且 `part1` 仍只覆盖 self profile 与最小设置宿主。当前 step 复用 step-01 的资料宿主与 `packages/api_contracts` 导出链路，不新增新的 `libs/` 共享层前置 change。

## 本次变更包含什么

- 提供 `PATCH /users/me` 或等价的自我资料更新入口
- 限定可编辑字段白名单、格式校验和空值处理语义
- 保证 `auth` 拥有的手机号、登录状态等字段不被 `users` 写入覆盖

## 本次变更不包含什么

- 偏好、通知与隐私设置写入
- 后台用户管理或状态治理
- 媒体上传链路与对象存储资源创建

## 预期结果

1. 已登录用户可以通过受控入口更新自己的基础资料。
2. `users` 与 `auth` 的字段边界不会因资料编辑再次混淆。
3. 后续移动端或后台前台接入可以复用稳定的资料写入契约。

## 影响范围

- `apps/api/src/modules/users/*`
- `apps/api/src/modules/auth/*`
- `packages/api_contracts/openapi/openapi.json`
