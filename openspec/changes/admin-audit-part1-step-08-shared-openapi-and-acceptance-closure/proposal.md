# 变更提案：Admin Audit Part1 Step 08 共享 OpenAPI 与验收收口

## 为什么要做

在 step-05 到 step-07 逐步收口后台用户读取门禁、用户治理状态机和审计查询边界之后，`admin-audit-part1` 还需要一个明确的“共享契约 + 测试验收”收口 step，避免再次出现运行时行为、Swagger 注解、生成产物和集成测试互相漂移的情况。

这次验收已经暴露出两类典型问题：

- ban / unban 的实际 HTTP 状态码和当前控制器契约注解不一致
- `admin-users` 与 `admin-agents` 集成测试没有随着 `AdminGuard` 依赖图更新，导致套件在 TestingModule compile 阶段直接失败

本 step 继续沿用 `admin-audit-part1` 作为 series prefix，只处理共享 OpenAPI 契约同步与 admin 系列验收收口，不再引入新的 admin 业务能力。

## 本次变更包含什么

- 对齐后台用户治理接口的真实 HTTP 语义与 Swagger / OpenAPI 契约
- 修复 `admin-users`、`admin-agents` 等受影响测试套件的 guard 依赖装配，让 admin 套件能真实跑通
- 执行 `openapi-export` 或等价导出流程，刷新共享 OpenAPI 产物并记录验收结果

## 本次变更不包含什么

- 新的后台用户治理能力
- 新的审计记录类型或查询字段
- 新的后台 Agent 治理能力

## 预期结果

1. `admin-audit-part1` 已交付路径的运行时状态码、Swagger 注解和共享 OpenAPI 产物保持一致。
2. `admin-users` 与 `admin-agents` 等受影响 admin 套件不再因为过期的 guard 依赖装配而在模块构建阶段失败。
3. `admin-audit-part1` 系列完成一轮可复用的契约与验收收口。

## 影响范围

- `apps/api/src/modules/admin/*`
- `apps/api/src/modules/admin/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- 必要时的 `docs/api/*`

