# 变更提案：Mobile Auth Step 02 验证码登录与会话建立

## 为什么要做

`mobile-auth-step-01` 解决的是“能否进入 mobile 认证入口并发出验证码请求”，但它还没有闭合真正的登录主路径。

当前 mobile 端虽然已经具备 `SessionSnapshot`、`SessionStorage` 和 `AuthStateOwner` 这些 foundation 原语，但还没有：

- 消费 `/auth/login` 的验证码登录结果
- 把 tokens / userId 写入本地会话快照
- 通过受控边界把 access token 带入后续受保护请求
- 在登录成功但协议未齐备时阻止用户直接进入完整产品空间

如果这一步不单独补齐，后续协议 gating、refresh 和设备会话都会缺少真实的“已建立 mobile 会话”前置状态。

## 本次变更包含什么

本次变更聚焦验证码登录成功后的 mobile 会话建立，范围包括：

- 接入 `/auth/login` 共享 HTTP contract，完成验证码登录提交
- 将成功结果写入 `SessionSnapshot` 并更新 `AuthStateOwner`
- 提供最小受控 auth header 注入边界，供后续受保护 auth 请求复用
- 在登录成功但 `gating.canAccessFullProduct=false` 时，把用户导向受控的 gated pending 边界，而不是直接放入完整产品空间
- 对登录失败错误码、剩余尝试次数和加载状态提供统一反馈

## 本次变更不包含什么

本次变更不包含以下内容：

- 完整的协议确认页面与录入流程
- access token 过期后的自动 refresh 与请求重放
- 设备会话列表、移除会话或退出登录页面
- 第三方登录或账号注册表单

## 预期结果

完成后，项目应具备以下结果：

1. 用户可以在 mobile 端输入验证码并完成首期 OTP 登录
2. 登录成功后，mobile 会拥有可恢复的本地会话快照，而不是停留在一次性页面状态
3. 登录返回 gating 未放行时，用户会进入受控等待边界，而不是误入完整产品空间
4. 后续 step 可以在已建立的 mobile 会话之上补协议 gating、refresh 和设备会话管理

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/features/auth/*`
- `apps/mobile/lib/core/auth/*`
- `apps/mobile/lib/core/network/*`
- `apps/mobile/lib/app/routing/*`
- `apps/mobile/test/features/auth/*`
- `apps/mobile/test/core/auth/*`
- `apps/mobile/README.md`
