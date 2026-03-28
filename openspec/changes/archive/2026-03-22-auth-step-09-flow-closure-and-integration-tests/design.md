# 设计说明：Auth Step 09 主流程收口与集成测试补强

## 目标

这个 step 不解决“auth 还能扩哪些能力”，而是解决“当前对外已经暴露出来的 auth 是否足够清晰、稳定、可回归验证”。

重点有四件事：

1. 收敛公开 OTP 登录主路径
2. 收敛手机号规范化规则
3. 细化 refresh 失败语义
4. 为 auth HTTP 边界补真实回归测试

## 边界

本次设计覆盖：

- `auth` controller 的公开 HTTP 合同
- OTP 验证与会话创建之间的公开流程衔接
- 大陆手机号输入格式到内部 canonical format 的收敛
- refresh token 错误结果的最小语义拆分
- auth 的 controller / guard / validation 集成测试

本次设计不覆盖：

- 全局 `main.ts` 级 ValidationPipe / Guard 改造
- 风控模型整体重构
- `apps/api` 其他模块的 HTTP 集成测试体系
- 多国家区号与国际化手机号

## 设计思路

### 1. 公开 OTP 登录主路径只保留可完成会话建立的入口

当前 `otpService.verifyLoginOtp()` 本来是 auth 领域内部能力，适合被 `/auth/login` 复用。

问题在于 controller 又把 `/auth/otp/verify` 作为公开接口暴露出来，且文案会让调用方误以为它可以作为“先验码、后登录”的第一步，但当前并不存在公开的后续 exchange 合同。

本 step 建议：

- 将“消费 OTP 并建立登录态”的公开主路径明确收敛到 `/auth/login`
- 不再把 `/auth/otp/verify` 作为对外推荐或默认可用的公共登录入口
- 若代码复用需要保留 `verifyLoginOtp()`，则保留在 service 层，不再让公共 HTTP contract 暴露半流程承诺

这比临时拼一个新的 exchange token 机制更小，也更符合当前仓库“先把真相源收紧，再继续长功能”的节奏。

### 2. 手机号对外接受常见格式，但内部只保留一种 canonical format

当前 auth 实际上已经隐含“大陆手机号作为唯一身份锚点”的前提，但输入与内部格式还不够统一。

本 step 建议：

- auth 请求入口接受常见大陆手机号输入格式，例如：
  - `13800138000`
  - `138 0013 8000`
  - `138-0013-8000`
  - `+86 138 0013 8000`
- 在进入 auth 领域后统一归一为 `11` 位大陆手机号格式
- 短信发送侧继续在适配器命令里补 `+86`，而不是把 `+86` 作为 auth 内部主格式

这样可以同时满足：

- 前端输入足够友好
- cache key、OTP 校验、用户查找和建会话使用单一格式
- 对外短信发送仍走标准 E.164 风格拼接

### 3. refresh 失败语义至少拆成 expired 与 invalid

当前 refresh 流程把 JWT 校验阶段的所有异常都收敛成“已过期”，这会把几类不同问题混在一起：

- 真正过期
- token 被篡改
- token 结构错误
- 使用了错误 secret 或错误类型 token

本 step 建议：

- JWT 明确过期时返回 `REFRESH_TOKEN_EXPIRED`
- 其他签名/格式类失败返回 `INVALID_REFRESH_TOKEN`
- session 已撤销、token reuse 等既有业务错误保持现状

这样不需要一次性重做全量错误码，但可以把最常见的 refresh 判断分清。

### 4. 补“窄而准”的 auth HTTP 集成测试

当前 auth 测试主要集中在 service unit test，优点是快，但对下面这些问题不敏感：

- controller 是否真的挂了 `ValidationPipe`
- guard 是否真的接在路由上
- 401 / 400 / 200 的 HTTP 行为是否与 contract 一致
- DTO、controller、service 之间的 wiring 是否回归

本 step 建议新增一组聚焦 auth 的 HTTP 集成测试，采用 Nest `createNestApplication()` + `supertest`，但不强依赖完整真实基础设施。

建议覆盖：

- `/auth/login`
  - 成功登录
  - 验证码业务失败
  - body 缺字段或格式错误时返回 400
- `/auth/refresh`
  - refresh 成功
  - expired 与 invalid 分流
- 受保护接口
  - 未带 token 返回 401
  - revoked session 返回 401
  - 正常 token 可访问

这样既能验证 HTTP 边界，又不会把本次小 change 扩成全栈联调工程。

## 关键失败场景

- 如果只是把 `/auth/otp/verify` 文案改弱，但路由仍然公开且继续消耗 OTP，客户端误用问题不会真正消失
- 如果手机号 canonical format 不明确，修了 `+86` 之后仍可能在 repository、cache 或短信发送上反复打架
- 如果 refresh 错误语义不拆，HTTP 测试补上后客户端仍然拿不到正确失败上下文
- 如果只补 unit test，不补 HTTP 集成测试，后续 controller 层仍可能再出现 wiring 回归

## 与现有实现边界的关系

这个 step 延续 Step 08 的思路：先在 `auth` 层局部收口，而不是急着把所有 NestJS 横切能力全局化。

这里的核心判断是：

- “auth 公开主路径是什么”“auth 接受什么手机号格式”“auth 受保护接口如何返回 401/400”本来就是 auth 自己的边界问题
- 这些问题先在 auth 模块内收紧，范围可控，也更容易指导当前阶段的开发机稳定实现

等 `apps/api` 更多模块成熟后，再考虑全局 ValidationPipe、统一错误格式或更系统的鉴权默认策略，会更稳。
