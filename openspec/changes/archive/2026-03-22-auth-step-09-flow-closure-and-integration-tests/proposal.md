# 变更提案：Auth Step 09 主流程收口与集成测试补强

## 为什么要做

`auth-step-08` 已经把守卫接线、会话撤销校验和最小请求校验补上，`auth` 模块的基础安全性明显提升了。

但最近一轮完整 review 也暴露出几类更偏“流程闭环”和“HTTP 边界可信度”的问题：

- `/auth/otp/verify` 仍以公开接口形式存在，但成功后会消耗验证码，却没有继续建立登录态的公开后续步骤，容易把客户端带进死胡同
- 手机号输入目前对 `+86`、空格、短横线等常见格式不够友好，外部输入格式与内部规范化格式还没有完全收拢
- refresh token 的错误结果仍偏粗，客户端很难区分“自然过期”和“无效/损坏 token”
- 目前 `auth` 测试仍以 service unit test 为主，controller / pipe / guard / 路由 wiring 这类 HTTP 边界行为缺少真正的集成级回归保护

这些问题不需要重写整个认证体系，但如果继续放着：

- 前端或其他调用方会对 auth 的公开主路径产生误解
- 常见输入格式会变成无意义的联调噪音
- refresh 失败的客户端处理和排查上下文会长期模糊
- 后续再有低质量实现接手 auth 时，更容易在 controller 层回归

因此需要一个新的小 step，把 `auth` 对外最容易让人误用或误判的部分再收紧一轮。

## 本次变更包含什么

本次变更聚焦 `auth` 的主流程收口与 HTTP 边界补强，范围包括：

- 收敛公开手机号验证码登录主路径，避免公开暴露“消耗 OTP 但不建立登录态”的半流程接口
- 明确并实现 auth 领域的手机号规范化规则，接受常见大陆手机号输入格式并统一为单一内部格式
- 细化 refresh token 错误结果，至少区分“已过期”和“无效/损坏”
- 为 auth controller 增加聚焦的 HTTP 集成测试，覆盖校验、守卫、刷新和会话撤销等关键边界
- 如对外 contract 发生变化时同步 `openapi-export`

## 本次变更不包含什么

本次变更不包含以下内容：

- 重做验证码发送、验证码缓存或双令牌签发主算法
- 一次性补完整风控平台或把 Step 07 的全部风控逻辑重构
- 将 `ValidationPipe`、`AuthGuard` 等能力全局化到整个 `apps/api`
- 引入第三方登录、邮箱登录或多地区手机号能力
- 重做整个 `auth` 错误码体系

## 预期结果

完成后，项目应具备以下结果：

1. 面向客户端的 OTP 登录路径会更清晰，不再公开暴露会把调用方卡住的半流程入口
2. 常见大陆手机号输入格式能稳定通过 auth 入口并收敛成统一内部格式
3. refresh 失败结果对客户端和排查更可解释
4. auth 的 HTTP 边界会有一层真实集成测试兜底，而不只依赖 service mock 单测

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/auth/auth.controller.ts`
- `apps/api/src/modules/auth/otp.service.ts`
- `apps/api/src/modules/auth/session.service.ts`
- `apps/api/src/modules/auth/cache/auth-cache.service.ts`
- `apps/api/src/modules/auth/__tests__/*`
- `apps/api/test/*` 或新的 auth HTTP 集成测试文件
- 如对外 HTTP contract 变化时对应的 `packages/api_contracts/openapi/openapi.json`
