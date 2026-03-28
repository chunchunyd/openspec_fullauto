# 设计说明：API Swagger 与 OpenAPI 导出基线

## 目标

这个 step 只解决 API contract 的文档生成与导出基线：

1. API 侧 Swagger / OpenAPI 真相源接线
2. 本地开发可查看的文档入口
3. `openapi-export` 的稳定原始 JSON 来源

## 当前约束

- 当前仓库已经有 `openapi-export` 脚本，但 API 侧 Swagger 接线并未在当前 change 计划中被单独收敛
- `infra/scripts/openapi-export.sh` 当前默认抓取 `http://localhost:3000/api-json`
- `auth-mobile-step-*` 需要在消费 API 前先依赖稳定的共享 contract 导出链路

## 建议接线

建议在 `apps/api` 中采用 Nest 官方 Swagger 接线，至少形成：

- 一个开发联调可访问的 Swagger UI 入口
- 一个供导出脚本读取的原始 OpenAPI JSON 入口

为了兼容当前脚本，原始 JSON 入口建议继续保持：

- `/api-json`

Swagger UI 入口建议明确为：

- `/api-docs`

## 生成链路

```text
Nest route metadata and DTO truth source
    ->
Swagger / OpenAPI document builder
    ->
local docs endpoint and raw json endpoint
    ->
openapi-export script
    ->
packages/api_contracts/openapi/openapi.json
```

## 环境边界

- 开发与联调环境应默认可访问 Swagger UI 与 raw JSON
- 生产环境是否暴露 UI 可以通过配置收口，但不应影响导出链路
- `openapi-export` 应始终以同一份 Swagger / OpenAPI 文档为来源，不要再维护第二套手工 JSON

## 与 mobile auth 的关系

- `auth-mobile-step-01-shell-routing-and-auth-state-foundation` 开始前，应先完成本 change
- 后续 `auth-mobile-step-02` 及之后的页面接入，都应以该 change 产出的共享 contract 为字段依据

## 失败语义

- 如果 API 未暴露 raw JSON 入口，`openapi-export` 应明确失败
- 不应导出空文件、旧文件或无法解释的残缺产物来冒充成功
