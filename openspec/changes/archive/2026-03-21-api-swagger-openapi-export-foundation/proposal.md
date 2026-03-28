# 变更提案：API Swagger 与 OpenAPI 导出基线

## 为什么要做

当前仓库已经有根级 `openapi-export` 脚本和 `packages/api_contracts/openapi/openapi.json` 产物落位，但 API 侧还没有明确、稳定的 Swagger / OpenAPI 真相源接线说明。

这会带来两个直接问题：

- `mobile` 和 `admin-web` 虽然需要消费共享 contract，但导出链路缺少明确的 API 文档生成基线
- 后续 `auth-mobile-step-*` 在开始前，无法确定应该依赖哪条稳定的导出路径

尤其现在准备推进 mobile auth，如果不先把 Swagger 与 OpenAPI 导出这一步单独收敛出来，前端很容易重新回到“口头约定字段”的老路上。

因此需要先补一个前置 change，把 API 的 Swagger / OpenAPI 生成与导出基线稳定下来。

## 本次变更包含什么

本次变更聚焦 API contract 的文档与导出基线，范围包括：

- 在 `apps/api` 中引入 Swagger / OpenAPI 文档生成接线
- 为本地开发或联调环境暴露可查看的 Swagger 文档入口
- 为 `openapi-export` 提供稳定的原始 OpenAPI JSON 来源
- 让共享契约产物继续稳定写入 `packages/api_contracts/openapi/openapi.json`
- 明确 mobile / admin-web 在正式接入前依赖这条导出链路

## 本次变更不包含什么

本次变更不包含以下内容：

- `auth` 具体接口实现
- `mobile` 或 `admin-web` 的页面接入
- 基于 OpenAPI 的 Flutter client 生成体系
- 更复杂的 CI 契约漂移检查

## 预期结果

完成后，项目应具备以下结果：

1. API 拥有明确的 Swagger / OpenAPI 文档生成入口
2. `openapi-export` 不再依赖隐含前提，而是有稳定的原始导出来源
3. `mobile` auth 可以在此之后依据共享 contract 正式推进
4. 前后端字段对齐将优先基于导出的共享契约，而不是口头约定

## 影响范围

本次变更主要影响：

- `apps/api` 的应用启动与 API 文档接线
- `infra/scripts/openapi-export.sh`
- `packages/api_contracts/openapi/openapi.json`
- `docs/api/` 或等价 API 文档入口
