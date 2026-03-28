# 任务拆解：Mobile Auth Step 01 登录入口与验证码发送

## 1. 实施前门禁

- [x] 如果 `dev-mobile-auth` 不存在，则从最新 `dev` 切出 `dev-mobile-auth`（注：Git 不允许 `dev/mobile-auth` 因为 `dev` 已存在）
- [x] 从 `dev-mobile-auth` 切出 `feat/mobile-auth-step-01-login-entry-and-otp-send`
- [x] 确认 `mobile-foundation-step-01` 至 `step-05` 已归档且当前实现可复用
- [x] 确认当前 step 只建立登录入口与验证码发送，不混入登录态建立、协议 gating、refresh 和设备会话管理

## 2. 契约与前置共享层检查

- [x] 阅读 `packages/api_contracts/openapi/openapi.json` 中 `/auth/otp/send` 的请求、响应和错误码，确认 mobile 消费字段
- [x] 检查 mobile 侧是否已有可复用的设备上下文、installation id 或等价适配边界；如果没有，补最小 auth 范围适配而不是把这些字段散落到页面
- [x] 如果发现共享 OpenAPI 契约与 `apps/api` 当前 controller 漂移，先回补契约或拆前置 API change，不长期依赖口头字段约定

## 3. 登录入口与发送流程

- [x] 将 auth 空间收敛为手机号验证码登录主入口，移除或重定向误导性的注册占位页
- [x] 建立手机号输入、基础格式校验、提交禁用和错误提示边界
- [x] 接入 `/auth/otp/send` 请求，并将成功、冷却、频控、风险限制和短信失败映射到统一反馈原语
- [x] 实现发送后的倒计时、重发门禁和请求中状态，避免页面层直接散落计时逻辑

## 4. 文档与注释

- [x] 更新 `apps/mobile/README.md` 或等价 auth 模块说明，记录当前 auth 入口职责和非目标
- [x] 对 auth 入口、OTP 发送状态和设备上下文字段边界补必要注释

## 5. 验证与测试

- [x] 为手机号输入校验、发送成功、冷却和失败映射补单元测试或 widget 测试
- [x] 验证 auth 入口在 foundation 反馈组件和错误映射下能稳定展示发送结果
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. 用户进入 auth 入口后，应看到手机号验证码登录主路径，而不是继续暴露注册占位页
2. 输入合法手机号并请求验证码后，应出现倒计时与重发门禁
3. 命中冷却、频控或风险限制时，页面应显示受控反馈，而不是泄露原始底层错误

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-auth-step-01-login-entry-and-otp-send` squash merge 回 `dev-mobile-auth`
- [x] 不在本 change 内执行 `dev-mobile-auth -> dev`，该操作由人工负责
