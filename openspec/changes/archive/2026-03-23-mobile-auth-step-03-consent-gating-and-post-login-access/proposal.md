# 变更提案：Mobile Auth Step 03 协议确认 gating 与登录后放行

## 为什么要做

`mobile-auth-step-02` 已经能让 mobile 端建立本地会话，但它只是在登录返回 `gating` 未放行时把用户停在受控 pending 边界，并没有真正完成协议确认流程。

而当前后端已经具备：

- `GET /auth/consent/status`
- `POST /auth/consent/record`
- `POST /auth/consent/record-all`

如果 mobile 端迟迟不接这条链路：

- 已登录但未完成协议确认的用户会被长期卡在临时边界
- 启动恢复后无法稳定判断当前 session 是否已经可访问完整产品
- 路由放行与协议状态会长期依赖上一次登录结果，而不是服务端当前真相

因此需要把 mobile 端的协议确认 gating 单独拆成一个 step。

## 本次变更包含什么

本次变更聚焦协议确认 gating 与登录后放行，范围包括：

- 为已登录但未完成协议确认的用户建立正式 consent gate 页面或等价受控边界
- 接入 `/auth/consent/status`，在登录后与启动恢复后都能获取当前 gating 真相
- 接入 `/auth/consent/record-all` 或受控的单项确认流，完成首期必要协议确认
- 让 auth 空间、gated 空间与完整产品空间之间的路由分流可解释、可重复

## 本次变更不包含什么

本次变更不包含以下内容：

- refresh token 自动续期
- 设备会话管理与退出登录
- 协议正文内容管理后台
- 第三方登录或更复杂的 onboarding 表单

## 预期结果

完成后，项目应具备以下结果：

1. 已登录但未完成协议确认的用户可以在 mobile 端完成首期必要确认，而不是停在临时占位边界
2. 应用启动恢复后能够从服务端重新确认当前 session 是否已被放行进入完整产品
3. 登录后放行不再只依赖一次性登录返回，而能与服务端最新 gating 状态保持一致

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/features/auth/*`
- `apps/mobile/lib/app/routing/*`
- `apps/mobile/lib/core/auth/*`
- `apps/mobile/lib/core/network/*`
- `apps/mobile/test/features/auth/*`
- `apps/mobile/README.md`
