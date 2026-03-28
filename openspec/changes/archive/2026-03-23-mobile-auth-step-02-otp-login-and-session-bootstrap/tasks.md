# 任务拆解：Mobile Auth Step 02 验证码登录与会话建立

## 1. 实施前门禁

- [x] 同步最新 `dev/mobile-auth`
- [x] 从 `dev/mobile-auth` 切出 `feat/mobile-auth-step-02-otp-login-and-session-bootstrap`
- [x] 确认 `mobile-auth-step-01-login-entry-and-otp-send` 已完成或达到可复用状态
- [x] 确认当前 step 只建立验证码登录后的 mobile 会话，不混入正式协议确认、refresh 和设备会话管理

## 2. 契约与共享层检查

- [x] 阅读 `packages/api_contracts/openapi/openapi.json` 中 `/auth/login` 的请求、响应、gating 字段和错误码
- [x] 检查 `SessionSnapshot`、`SessionStorage`、`AuthStateOwner` 与 `ApiClient` 的现有边界是否足以复用；若有缺口，只补最小扩展
- [x] 确认 auth header 注入边界不会绕开统一 request pipeline，也不会在页面层直接拼 Authorization header

## 3. 登录提交与会话写入

- [x] 建立验证码输入、提交中状态、剩余尝试次数和错误提示的受控交互
- [x] 接入 `/auth/login` 并映射登录成功、验证码错误、风控限制和账号受限等业务结果
- [x] 在登录成功时写入 `SessionSnapshot`、更新 `AuthStateOwner`，并确保后续启动恢复可读到同一会话
- [x] 为显式需要 bearer 的 auth 请求接入最小 access token 注入边界，但暂不实现 refresh

## 4. 路由与 gated pending 边界

- [x] 在登录成功且 `gating.canAccessFullProduct=true` 时进入正常产品入口
- [x] 在登录成功但 `gating.canAccessFullProduct=false` 时进入受控的 consent-required pending 边界，而不是直接放进完整产品空间
- [x] 保持 auth 路由守卫与 foundation `AuthStateOwner` 的语义一致，不重建另一套并行登录态

## 5. 文档与注释

- [x] 更新 `apps/mobile/README.md` 或等价 auth 文档，说明 mobile 会话建立与 gated pending 边界
- [x] 对登录结果映射、session 写入和 auth header 注入边界补必要注释

## 6. 验证与测试

- [x] 为 `/auth/login` 成功、业务失败、session 持久化和 gated pending 分流补单元测试或 widget 测试
- [x] 验证应用重启后可以从已写入的 session snapshot 恢复最小已登录状态
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. 用户输入正确验证码后，应能建立本地会话并离开 OTP 输入态
2. 登录返回 `gating.canAccessFullProduct=false` 时，用户不应被直接导入完整产品空间
3. 登录失败时，应展示与后端错误码对应的受控反馈，而不是底层 transport 异常

## 7. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-auth-step-02-otp-login-and-session-bootstrap` squash merge 回 `dev/mobile-auth`
- [x] 不在本 change 内执行 `dev/mobile-auth -> dev`，该操作由人工负责
