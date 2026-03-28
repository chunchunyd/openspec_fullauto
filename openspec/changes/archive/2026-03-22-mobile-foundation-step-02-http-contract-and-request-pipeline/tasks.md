# 任务拆解：Mobile Foundation Step 02 HTTP 契约与请求管线

## 1. 实施前门禁

- [x] 同步最新 `dev/mobile-foundation`
- [x] 从 `dev/mobile-foundation` 切出 `feat/mobile-foundation-step-02-http-contract-and-request-pipeline`
- [x] 确认 `mobile-foundation-step-01-app-shell-entry-boundary` 已完成或达到可复用状态
- [x] 确认最新 `packages/api_contracts/openapi/openapi.json` 可用；如果后端 contract 刚发生变化，先执行 `pnpm openapi-export`
- [x] 确认当前 step 只建立 contract 消费与 request pipeline，不混入 session storage、auth state 和页面 feedback primitives

## 2. 共享 HTTP contract 对齐

- [x] 明确 mobile 端请求字段、响应字段、状态码与错误结构以共享 OpenAPI 产物为依据
- [x] 决定 contract 消费的落位方式，并让 `apps/mobile/lib/core/network` 成为统一入口
- [x] 禁止后续页面或 feature 长期直接依赖服务端内部 DTO 或手写漂移字段

## 3. 请求管线与基础错误边界

- [x] 建立统一的 API client 入口、base URL 装配、header 处理与 timeout 策略
- [x] 建立网络异常、超时、4xx、5xx 的最小受控错误映射
- [x] 让 feature 通过统一请求管线访问底层 transport，而不是各自维护底层请求细节

## 4. 文档与注释

- [x] 更新 `apps/mobile/README.md`，说明 contract 基线、`openapi-export` 前置约束和 request pipeline 落位
- [x] 对错误映射或 request pipeline 中不直观的边界补必要注释，说明约束和非目标

## 5. 验证与测试

- [x] 为 base URL、header、timeout 与基础错误映射补单元测试或等价验证
- [x] 验证 contract 变化时 mobile 端以共享 OpenAPI 产物为依据，而不是继续沿用旧字段
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. mobile 端应能通过统一 API client 指向当前环境 API 基础地址
2. 请求超时、网络失败和服务端异常应被映射为受控错误结果，而不是直接向页面暴露底层原始错误
3. 字段对齐应以共享 OpenAPI 产物为准，而不是手写长期漂移 DTO

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-foundation-step-02-http-contract-and-request-pipeline` squash merge 回 `dev/mobile-foundation`
- [x] 不在本 change 内执行 `dev/mobile-foundation -> dev`，该操作由人工负责
