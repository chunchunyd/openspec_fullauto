# 变更提案：Users Part1 Step 06 共享 OpenAPI 契约与验收收口

## 为什么要做

上一轮对 `series/users-part1` 的验收表明，当前共享 OpenAPI 产物还没有覆盖 `/users/me` 与 `/users/me/settings` 这组已交付接口。即便 step-04 完成持久化历史收口、step-05 完成请求校验加固，如果没有把 users 自我资料与设置路径重新导出到 `packages/api_contracts/openapi/openapi.json`，前端和生成链路仍然只能依赖过期或缺失的共享契约继续联调。

本批 change 继续沿用 `users-part1` 作为 series prefix，并把这一步限制在共享 OpenAPI 契约同步与最终验收收口，不再引入新的 users 业务字段或数据库结构调整。

## 本次变更包含什么

- 审阅 users 自我资料与设置接口的 Swagger 注解与导出结果，确保共享 OpenAPI 可以表达代表性的成功、未认证和校验失败语义
- 执行 `openapi-export` 或等价导出流程，更新 `packages/api_contracts/openapi/openapi.json`
- 完成 `users-part1` 这一轮针对 self profile / settings 的最终验收收口，并记录导出与验证结果

## 本次变更不包含什么

- 新的资料字段、设置字段或 users 业务能力
- 新的 Prisma schema 或 migration 历史
- 额外的请求校验策略返工（除非导出结果暴露了明显缺口）

## 预期结果

1. `packages/api_contracts/openapi/openapi.json` 包含 `/users/me` 与 `/users/me/settings` 的当前已交付契约。
2. 共享契约能够体现这组路径的代表性成功、未认证与校验失败结果。
3. `users-part1` 当前围绕 self profile / settings 的主要 review 缺口完成统一收口。

## 影响范围

- `packages/api_contracts/openapi/openapi.json`
- 必要时的 `apps/api/src/modules/users/*` Swagger 注解与导出相关说明
- 必要时与 `openapi-export` 使用方式直接相关的文档入口
