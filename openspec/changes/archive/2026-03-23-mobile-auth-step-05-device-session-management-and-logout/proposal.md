# 变更提案：Mobile Auth Step 05 设备会话管理与退出登录

## 为什么要做

后端 auth 模块已经具备：

- `GET /auth/sessions`
- `POST /auth/sessions/remove`
- `POST /auth/logout`

但 mobile 端仍缺少用户可见的会话管理与退出登录闭环。这样会带来两个问题：

- 用户无法查看当前账号在哪些设备上保持登录态，也无法主动移除其他设备
- 当前设备没有完整的 logout 收口，session 只能依赖 token 失效或调试手动清理

在 mobile 基础 auth 已具备登录、gating 和 refresh 之后，这些能力可以被拆成独立的 settings / account step，而不需要继续塞回前面的登录链路。

## 本次变更包含什么

本次变更聚焦设备会话治理与当前设备退出登录，范围包括：

- 在 mobile 端建立设备会话列表入口，消费 `/auth/sessions`
- 展示当前设备标记、最近活跃时间和设备基础信息
- 接入 `/auth/sessions/remove`，允许用户移除其他设备会话
- 接入 `/auth/logout`，完成当前设备退出登录与本地 session 清理
- 对会话移除、当前设备 logout 和失败状态提供统一反馈

## 本次变更不包含什么

本次变更不包含以下内容：

- 账号注销
- 黑名单、免打扰或更完整的设置中心
- 新的风控策略或异地登录提醒

## 预期结果

完成后，项目应具备以下结果：

1. 用户可以在 mobile 端查看和管理自己的设备会话
2. 用户可以主动移除其他设备会话，并在当前设备执行退出登录
3. 当前设备 logout 后，mobile 会稳定清理本地 session 并退出受保护空间

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/features/auth/*`
- `apps/mobile/lib/app/routing/*`
- `apps/mobile/lib/core/auth/*`
- `apps/mobile/test/features/auth/*`
- `apps/mobile/README.md`
