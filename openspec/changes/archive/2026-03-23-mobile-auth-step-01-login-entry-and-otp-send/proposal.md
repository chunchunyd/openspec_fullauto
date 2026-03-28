# 变更提案：Mobile Auth Step 01 登录入口与验证码发送

## 为什么要做

`apps/mobile` 当前只有 foundation 层的路由壳、请求管线和最小认证状态原语，`/auth/login` 与 `/auth/register` 仍是占位页。

与此同时，`apps/api` 的手机号验证码认证主路径已经完成，且共享 OpenAPI 契约已经导出。如果 mobile 端继续停留在占位态：

- 首期公开认证入口仍然和真实后端主路径脱节
- 用户无法从 mobile 端发起验证码请求与倒计时流程
- 后续验证码登录、协议 gating、refresh 和设备会话管理都没有稳定入口宿主

因此需要先把 mobile 端的首期 auth 入口与验证码发送链路单独拆出来，形成后续 step 的公共起点。

## 本次变更包含什么

本次变更聚焦 mobile 首期公开认证入口，范围包括：

- 将 auth 空间从“登录/注册占位页”收敛为手机号验证码登录主入口
- 建立手机号输入、基础格式校验和发送按钮的受控交互
- 接入 `/auth/otp/send` 共享 HTTP contract，并映射成功、冷却、频控和风险错误反馈
- 建立验证码发送后的倒计时、重发门禁和基础页面反馈
- 检查 mobile 侧是否已有可复用的设备上下文或 installation id 边界；若缺失，则在 auth feature 范围内补最小适配

## 本次变更不包含什么

本次变更不包含以下内容：

- 验证码登录提交与会话建立
- token 持久化、auth header 注入或 refresh 流程
- 协议确认 gating
- 设备会话管理与退出登录
- 第三方登录或注册分流设计

## 预期结果

完成后，项目应具备以下结果：

1. mobile 端有一个与后端主路径一致的手机号验证码登录入口，而不是继续保留误导性的注册占位页
2. 用户可以在 mobile 端请求验证码，并看到一致的冷却、频控与失败反馈
3. 后续 step 可以复用稳定的 auth 页面壳、输入状态与 OTP 发送结果，而不是重新起一套入口

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/app/routing/*`
- `apps/mobile/lib/features/auth/*`
- `apps/mobile/lib/core/network/*`
- `apps/mobile/test/features/auth/*`
- `apps/mobile/README.md`
