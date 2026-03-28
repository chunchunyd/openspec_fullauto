# 变更提案：Public Content Step 17 共享 OpenAPI 契约收口

## 为什么要做

最新验收表明，`series/public-content` 虽然已经新增了 feed、content public detail、comments、follows、reports 等对外 HTTP 路径，但共享 OpenAPI 产物仍然停留在旧状态，`packages/api_contracts/openapi/openapi.json` 里看不到这些新路径。

这会让 mobile、admin-web 或其他消费方继续拿着过期契约联调，直接破坏当前仓库“API 真相源 -> openapi-export -> 共享契约产物”的协作链路。

本 step 继续沿用 `public-content` 作为 series prefix，只收口 public-content 已交付 HTTP 路径对应的共享 OpenAPI 导出，不扩展新的接口行为或 DTO 语义。

## 本次变更包含什么

- 重新执行 `openapi-export`，同步 `packages/api_contracts/openapi/openapi.json` 与 `docs/api/*`
- 核对 public-content 已交付公开路径是否都进入共享契约产物
- 对代表性成功 / 错误契约做最小 spot check，避免导出旧文件冒充成功

## 本次变更不包含什么

- 新的 public-content HTTP 接口
- 额外的 DTO 字段扩张
- runtime / gRPC 契约变更

## 预期结果

1. 共享 OpenAPI 产物能够覆盖当前已交付的 public-content 公开 HTTP 路径。
2. front-end 和其他消费方可以基于最新共享契约继续联调，而不是依赖口头约定或旧文件。
3. public-content 系列的 HTTP contract 交付链路重新闭环。

## 影响范围

- `packages/api_contracts/openapi/openapi.json`
- `docs/api/openapi.json`
- `docs/api/openapi.yaml`
- 必要时的 `infra/scripts/openapi-export.sh` 或等价导出说明
