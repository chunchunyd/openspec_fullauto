# Delta for API Contracts

## ADDED Requirements

### Requirement: API 服务必须提供可导出的 Swagger / OpenAPI 文档生成链路

系统必须在 API 服务中提供可导出的 Swagger / OpenAPI 文档生成链路，用于开发联调、共享契约导出和前后端字段对齐。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 本地开发查看 API 文档

- WHEN 开发者在本地启动 API 服务
- THEN 系统必须提供一个可访问的 Swagger 文档入口
- AND 开发者必须能够查看当前 HTTP contract 的主要结构

#### Scenario: 执行 openapi-export

- WHEN 开发者执行 `openapi-export`
- THEN 系统必须从 API 服务的 Swagger / OpenAPI 真相源生成 raw OpenAPI JSON
- AND 必须将共享契约产物更新到 `packages/api_contracts/openapi/openapi.json`

### Requirement: openapi-export 失败时不得产出冒充成功的坏契约文件

系统必须在 Swagger / OpenAPI 原始来源不可用时明确失败，而不是导出空文件、旧文件或残缺产物冒充成功结果。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 原始 OpenAPI JSON 来源不可用

- WHEN `openapi-export` 依赖的 Swagger / OpenAPI JSON 入口不可访问
- THEN 导出流程必须明确失败
- AND 不得把无效产物写成最新共享契约
