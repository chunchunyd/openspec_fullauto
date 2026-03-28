# 任务拆解：API Swagger 与 OpenAPI 导出基线

## 1. 实施前门禁

- [x] 从最新 `dev` 切出 `feat/api-swagger-openapi-export-foundation`
- [x] 阅读当前 `api-contracts` spec、`infra/scripts/openapi-export.sh` 和 `apps/api` 启动入口
- [x] 确认本 change 是 `auth-mobile-step-*` 前的前置能力，而不是和 mobile 页面接入混在同一个实现分支里

## 2. API Swagger 接线

- [x] 在 `apps/api` 中引入 Swagger / OpenAPI 文档生成能力
- [x] 建立统一的 document builder 配置
- [x] 暴露供开发联调使用的 Swagger UI 入口
- [x] 暴露与 `openapi-export` 兼容的 raw OpenAPI JSON 入口

## 3. 导出链路收敛

- [x] 让 `infra/scripts/openapi-export.sh` 明确依赖 Swagger raw JSON 入口
- [x] 确认导出产物稳定写入 `packages/api_contracts/openapi/openapi.json`
- [x] 如有需要，同步更新 `docs/api/` 或等价文档落位
- [x] 明确脚本失败时的退出语义，避免导出坏产物

## 4. 文档与协作约定

- [x] 更新 API 或根级 README / 文档，说明 Swagger UI 与 `openapi-export` 的使用方式
- [x] 在相关 mobile auth changes 中明确其前置依赖是本 change 产出的共享 contract

## 5. 验证与测试

- [x] 验证本地启动 API 后可以访问 Swagger UI
- [x] 验证执行 `openapi-export` 后能生成最新共享契约产物
- [x] 验证导出失败时脚本会明确报错，而不是静默成功

### 手动验收步骤

1. 启动 `apps/api` 后，应能访问 Swagger UI 和 raw OpenAPI JSON
2. 执行 `pnpm openapi-export` 后，应更新 `packages/api_contracts/openapi/openapi.json`
3. 在 Swagger 接线被故意移除或不可用时，导出脚本应明确失败
