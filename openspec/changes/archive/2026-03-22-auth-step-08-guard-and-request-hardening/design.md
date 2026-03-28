# 设计说明：Auth Step 08 鉴权守卫与请求校验加固

## 目标

这个 step 解决的是 `auth` 模块后置硬化问题，而不是重写主流程。

重点只有三件事：

1. 让受保护接口真正受保护
2. 让 access token 判定和会话撤销语义一致
3. 让明显坏请求在进入核心逻辑前被受控拦住

## 边界

本次设计覆盖：

- `auth` controller 中需要 access token 的接口
- `AuthGuard` 与 `SessionService` 的 access token 校验边界
- `auth` 请求 DTO 的最小运行时输入校验
- 与此直接相关的 Swagger / OpenAPI 语义和测试

本次设计不覆盖：

- 验证码算法和缓存语义调整
- refresh token 轮换策略重做
- `apps/api` 其他模块的统一请求校验改造
- 全局异常格式统一收敛

## 设计思路

### 1. 受保护接口在 controller 层显式挂守卫

当前 `auth` 中的协议确认、设备会话和退出登录接口已经在文档层声明 Bearer Auth，但运行时没有稳定守卫接线。

本 step 建议：

- 将 `AuthGuard` 正式注册到 `auth` 模块可用的 provider 图中
- 在 `auth.controller.ts` 中仅对真正需要 access token 的接口显式使用 `@UseGuards(AuthGuard)`
- 保持发码、登录、刷新、独立验证码校验这些公开入口不被误挂守卫

这样可以把“公开接口”和“受保护接口”的边界明确留在 controller，而不是只写在 Swagger 注释里。

### 2. access token 校验要联动会话状态

当前 access token 校验如果只验证 JWT 签名，会产生一个明显问题：

- refresh token 已经因为退出登录或设备移除失效
- 但旧 access token 仍可在有效期内继续访问受保护接口

本 step 建议把 access token 的运行时判定收敛成：

```text
Bearer token
    ->
verify JWT signature / expiry
    ->
extract sessionId + userId
    ->
lookup active session
    ->
confirm session belongs to same user and is still active
    ->
attach request.user
```

这样“退出登录”和“移除设备会话”对受保护接口访问就不再只是 refresh 侧语义，而能真正体现在 access token 判定中。

### 3. 请求校验先收敛在 auth 范围内

当前 `apps/api` 还处于早期阶段，一次性给整个应用打开全局请求校验，容易把范围扩散到其他尚未收敛的模块。

因此本 step 建议：

- 优先在 `auth` controller 范围内接入 `ValidationPipe`，或在 auth 相关入口按路由接入等价校验
- 在 `SendOtpRequestDto`、`VerifyOtpRequestDto`、`LoginRequestDto`、`RefreshTokenRequestDto`、`RecordConsentRequestDto`、`RecordAllConsentsRequestDto`、`RemoveSessionRequestDto` 上补最小 `class-validator` 规则
- 目标是让缺字段、类型错误、空字符串这类明显坏输入在进入 service 前失败

这个方案能把范围稳定控制在 `auth`，避免本次小 change 变成全站输入治理重构。

## 关键失败场景

- 如果只把 `UseGuards` 挂上，但 access token 仍不回查 session，退出登录后的访问控制仍然不完整
- 如果只补 DTO 类型，不补运行时 pipe，坏输入仍会穿透到 service
- 如果把全局 ValidationPipe 一次性打开，容易把本次补洞 change 扩成多模块返工
- 如果只修 lint，不补守卫和测试，后续仍会反复怀疑 auth 接口是否真的安全可用

## 与现有 specs 的关系

这个 step 不改变 `auth` 的业务主流程方向，而是把现有真相源中已经隐含的承诺补完整：

- 受保护接口必须基于登录态识别当前用户
- 被撤销的会话不应继续维持访问能力
- `auth` 主流程应返回可解释、可控的失败结果，而不是依赖未处理异常
