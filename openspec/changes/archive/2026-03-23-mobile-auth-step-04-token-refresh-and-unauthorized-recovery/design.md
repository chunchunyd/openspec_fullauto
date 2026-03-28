# 设计说明：Mobile Auth Step 04 Token Refresh 与未授权恢复

## 目标

本 step 的目标是让 mobile 端在 session 已建立的前提下，能够对 access token 过期做受控恢复，并在 refresh 不可恢复时稳定退出受保护空间。

本 step 只解决三个问题：

- 什么时候触发 refresh
- 多个请求同时命中 401 时如何串行化 refresh
- refresh 成功或失败后如何更新 session 与路由

## 非目标

本 step 不承担以下内容：

- 用户主动管理设备会话
- 生物识别、PIN 或本地二次验证
- 后台定时续期

## 核心边界

### Authenticated Request Interceptor

负责：

- 为受支持请求附加当前 access token
- 识别 401 / 等价未授权结果
- 将 refresh 协调交给专门的 refresh owner

它不直接读写页面状态，也不负责协议确认 UI。

### Refresh Owner / Coordinator

负责：

- 调用 `/auth/refresh`
- 将 refresh 过程串行化，避免并发重复刷新
- 成功时更新 `SessionSnapshot`
- 失败时清理 session 并通知路由层退出受保护空间

## 流程

```text
受保护请求
    │
    ▼
附加 access token
    │
    ▼
响应 401 ?
    │
 ┌──┴───┐
 │      │
否      是
 │      │
 ▼      ▼
返回结果 进入 refresh coordinator
              │
         ┌────┴─────────────┐
         │                  │
     refresh 成功       refresh 失败
         │                  │
         ▼                  ▼
更新 snapshot          清理 session
重放原请求             路由回到 auth
```

## Refresh 失败语义

以下情况都视为不可恢复，需要清理本地 session：

- `REFRESH_TOKEN_EXPIRED`
- `INVALID_REFRESH_TOKEN`
- `SESSION_REVOKED`
- `SESSION_NOT_FOUND`
- `TOKEN_REUSE_DETECTED`

区别在于用户反馈文案可以不同，但路由结果都不应继续保留受保护访问能力。

## 并发约束

为了避免多个请求同时命中 401 时各自刷新：

- refresh 过程必须串行化
- 正在等待 refresh 结果的请求应复用同一次 refresh 结果
- 一次 refresh 失败后，等待中的请求必须统一收到不可恢复结果，而不是各自继续重试

## 与前后 step 的关系

- `step-02` 已提供最小 auth header 注入
- `step-03` 已稳定 session、gated 和 full access 的放行边界
- 本 step 在此基础上补 token 续期与未授权恢复
- `step-05` 的设备会话与当前设备 logout 依赖本 step 提供稳定的受保护请求基线
