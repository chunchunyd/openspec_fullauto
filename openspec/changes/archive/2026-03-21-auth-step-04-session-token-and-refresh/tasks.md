# 任务拆解：Auth Step 04 会话令牌与刷新机制

## 1. 实施前门禁

- [x] 从最新 `dev` 切出 `feat/auth-step-04-session-token-and-refresh` 并确认主项目工作树边界
- [x] 确认 `auth-step-01` 和 `auth-step-03` 已完成或其数据 / 领域结果已可复用
- [x] 阅读当前 `auth` spec 与本 change 设计说明

## 2. 契约与会话边界

- [x] 为 `auth` capability 建立本次 step 的 spec delta
- [x] 定义 access token、refresh token 与会话记录之间的边界
- [x] 如新增对外接口 contract，执行 `openapi-export`

## 3. 会话签发与刷新

- [x] 基于已验证 auth 结果签发 access token 与 refresh token
- [x] 建立 refresh token 的持久化校验、撤销或轮换逻辑
- [x] 将签发结果与设备会话记录关联
- [x] 实现 refresh 接口或等价服务

## 4. 运行时接线

- [x] 补齐受保护接口识别当前用户的最小接线
- [x] 明确 refresh token 无效、过期或被撤销时的返回语义

## 5. 验证与测试

- [x] 为登录成功后建立会话补测试
- [x] 为 refresh 成功、refresh 无效、refresh 被撤销补测试
- [x] 验证 token 轮换或撤销后旧凭证不会继续稳定生效

### 手动验收步骤

1. 完成一次验证码登录后，应返回可用 access token 与 refresh token
2. 使用有效 refresh token，应得到新的认证结果
3. 使用无效或已撤销 refresh token，应被明确拒绝
4. 受保护接口应能基于登录态识别当前用户
