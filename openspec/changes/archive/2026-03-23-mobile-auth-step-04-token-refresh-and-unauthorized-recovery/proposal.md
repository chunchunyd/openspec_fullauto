# 变更提案：Mobile Auth Step 04 Token Refresh 与未授权恢复

## 为什么要做

完成 `mobile-auth-step-03` 后，mobile 端已经具备：

- 可恢复的本地 session
- 基本 bearer 注入边界
- 协议确认 gating 与登录后放行

但当前链路仍然缺少一个关键闭环：access token 过期后的受控恢复。

如果继续停留在“只会附加 access token，不会 refresh”的状态：

- 任意受保护请求命中 401 后都可能把用户直接打回登录页
- 并发请求命中过期时，容易产生重复 refresh 或状态竞态
- refresh token 已失效时，页面很难稳定清理本地 session 并回到 auth 空间

因此需要单独拆出一个 step，补齐 token refresh 与未授权恢复，而不是把这部分混进设备会话或其他设置类需求里。

## 本次变更包含什么

本次变更聚焦 mobile 端认证会话续期，范围包括：

- 接入 `/auth/refresh` 共享 HTTP contract
- 建立受控的 refresh 协调边界，避免并发 401 时无门禁地重复刷新
- 在 refresh 成功时更新本地 `SessionSnapshot` 并重放受支持请求
- 在 refresh token 过期、无效、已撤销或复用异常时清理本地 session 并退出受保护空间
- 为 401、refresh 成功与 refresh 失败建立统一的错误与反馈语义

## 本次变更不包含什么

本次变更不包含以下内容：

- 设备会话列表、移除设备或退出登录页面
- 生物识别解锁、本地 PIN 或离线加密容器
- 后台静默续期或 push 驱动的登录态同步

## 预期结果

完成后，项目应具备以下结果：

1. access token 过期时，mobile 端可以通过受控 refresh 续期，而不是把每次 401 都等价成重新登录
2. refresh 失败时，mobile 会清晰地清理本地 session 并退出受保护空间
3. 并发请求命中过期时，不会形成失控的重复 refresh 与状态踩踏

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/core/auth/*`
- `apps/mobile/lib/core/network/*`
- `apps/mobile/lib/features/auth/*`
- `apps/mobile/test/core/auth/*`
- `apps/mobile/test/core/network/*`
- `apps/mobile/README.md`
