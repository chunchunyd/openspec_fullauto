# 变更提案：Auth Step 08 鉴权守卫与请求校验加固

## 为什么要做

当前 `auth` 模块的主流程已经基本成形，但最近一轮检查暴露出一组更适合用“小补洞 change”收敛的问题：

- 一批标记为需要登录态的接口只有 `@ApiBearerAuth()` 文档标记，还没有真正挂上运行时鉴权守卫
- access token 当前主要只校验 JWT 本身，尚未把会话撤销状态稳定纳入受保护接口判定
- `auth` 请求 DTO 主要只有 Swagger 文档装饰器，缺少最小运行时输入校验，畸形请求容易落成 500 而不是明确失败
- `auth` 目录还残留少量 ESLint 噪音，容易掩盖真正的问题

这些问题本身不值得重新拆回验证码、会话或协议 step，但如果继续放着不收敛，会直接影响：

- 设备会话移除和退出登录的真实性
- 受保护接口的访问控制可信度
- 联调时对错误来源的判断
- 后续继续维护 `auth` 模块时的信心

因此需要补一个聚焦的小 step，把“受保护接口真的受保护”“坏请求不会轻易炸成 500”“auth 检查结果重新变得可信”这几件事收拢完成。

## 本次变更包含什么

本次变更聚焦 `auth` 模块的守卫与请求硬化，范围包括：

- 为 `auth` 中已声明需要登录态的接口接入真正的运行时鉴权守卫
- 让 access token 校验不仅验证 JWT，还校验关联会话是否仍然有效
- 为 `auth` 请求补最小运行时输入校验，避免明显坏输入直接打成未处理异常
- 在需要时补充 Swagger / OpenAPI 中的 401 / 校验失败语义并执行 `openapi-export`
- 清理本轮发现的 `auth` 目录 ESLint 噪音
- 补充守卫、会话撤销和请求校验相关测试

## 本次变更不包含什么

本次变更不包含以下内容：

- 重新设计验证码发送、验证码校验或双令牌签发主流程
- 扩展第三方登录
- 重做全站统一鉴权体系
- 一次性为整个 `apps/api` 打开全局 ValidationPipe 并波及所有早期模块
- 重新设计 `auth` 全量错误码体系

## 预期结果

完成后，项目应具备以下结果：

1. `consent`、设备会话和退出登录等受保护接口会真正要求有效 access token
2. 已撤销或已失效会话对应的 access token 不再继续访问受保护接口
3. `auth` 畸形请求会得到明确失败结果，而不是更容易落成 500
4. `auth` 目录的检查结果会重新回到“lint 干净、测试能解释行为”的状态

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/auth/auth.controller.ts`
- `apps/api/src/common/guards/auth.guard.ts`
- `apps/api/src/modules/auth/auth.module.ts`
- `apps/api/src/modules/auth/session.service.ts`
- `apps/api/src/modules/auth/dto/*`
- `apps/api/src/modules/auth/__tests__/*`
- 如对外 HTTP contract 发生变化时对应的 `packages/api_contracts/openapi/openapi.json`
