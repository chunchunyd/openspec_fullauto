# 变更提案：Admin Audit Part1 Step 02 审计中心读取边界

## 为什么要做

当前仓库里的 `audit` 已经有权威审计写入基础，但后台还没有正式的审计中心读取边界。作为 `admin-audit-part1` 的低耦合并行 step，本次只补齐后台查询审计记录的最小能力，让后续治理动作、复盘与责任追踪有稳定的读取出口。

本批 change 继续沿用 `admin-audit-part1` 作为 series prefix，且 `part1` 仍只覆盖后台入口、审计读取与用户治理最小骨架。当前 step 复用现有 `audit-log` 主存储、后台鉴权链路与 `packages/api_contracts` 导出链路，不新增新的 `libs/` 共享层前置 change。

## 本次变更包含什么

- 为后台审计中心建立最小查询、筛选、分页与排序边界
- 复用现有权威审计记录主存储，不重新定义 analytics 派生表
- 明确读取结果中的最小上下文字段与敏感信息处理

## 本次变更不包含什么

- 新的审计写入类型或治理动作改造
- 异常告警系统、实时监控或复杂报表
- 后台前端页面实现

## 预期结果

1. 后台可以通过正式接口查询关键审计记录。
2. 审计中心读取不会与 analytics 或调试日志 owner 混淆。
3. 后续治理动作可以直接接入同一条可追溯读取主线。

## 影响范围

- `apps/api/src/modules/audit/*`
- `apps/api/src/modules/admin/*`
- `packages/api_contracts/openapi/openapi.json`
