# 设计说明：Mobile Auth Step 02 验证码登录与会话建立

## 目标

本 step 的目标是在 mobile 端把“验证码发送成功”推进到“可恢复的已登录会话”，同时保证协议未完成的用户不会被直接放进完整产品空间。

本 step 只解决四个问题：

- 验证码登录请求由谁发起和消费
- 登录成功后由谁写入本地会话快照
- 后续受保护 auth 请求如何获得当前 access token
- 登录结果显示为 gated 时如何进入受控等待边界

## 非目标

本 step 不承担以下内容：

- 协议确认页的正式 UI 与录入动作
- access token 过期后的自动 refresh
- 设备会话管理
- 全站受保护接口的统一 401 恢复策略

## 边界划分

### Auth Feature

`features/auth` 负责：

- 验证码输入与登录提交状态
- `/auth/login` 响应映射
- 登录成功后的路由分流

它不直接管理底层 secure storage key，也不自行拼接 Authorization header。

### Foundation Auth

`core/auth` 继续负责：

- `SessionSnapshot` 模型
- `SessionStorage` 持久化
- `AuthStateOwner` 的状态 owner 语义

本 step 复用这些原语，不重建另一套 session owner。

### Network Boundary

本 step 引入最小 auth header 注入边界：

- 只负责从 `AuthStateOwner` 读取当前 access token
- 只对显式需要 bearer 的请求附加 `Authorization`
- 不在本 step 处理 refresh、重试或请求重放

## 状态流转

```text
手机号 + 验证码
        │
        ▼
POST /auth/login
        │
   ┌────┴─────────────────────┐
   │                          │
成功                      业务失败
   │                          │
   ▼                          ▼
写入 SessionSnapshot       展示受控错误反馈
更新 AuthStateOwner
   │
   ▼
读取 gating.canAccessFullProduct
   │
   ├─ true  -> 进入 full-product 可达路由
   └─ false -> 进入 consent-required pending 边界
```

## Gated Pending 边界

为了避免在协议尚未完成时误入完整产品空间，本 step 只引入一个最小 pending 边界：

- 登录成功且 `gating.canAccessFullProduct=true`：正常进入后续产品入口
- 登录成功但 `gating.canAccessFullProduct=false`：进入受控的 consent-required 页面或等价占位边界

这个 pending 边界只表达“当前已登录但还不能放行完整产品”，正式协议确认 UI 由下一 step 承接。

## 与后续 step 的关系

- `step-01` 提供登录入口与 OTP 发送
- 本 step 提供 OTP 登录成功后的 mobile 会话建立
- `step-03` 在 gated pending 边界上补正式协议确认流
- `step-04` 在当前 auth header 注入边界上补 refresh 与 401 恢复
