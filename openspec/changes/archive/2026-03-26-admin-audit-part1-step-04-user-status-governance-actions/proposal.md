# 变更提案：Admin Audit Part1 Step 04 用户状态治理动作

## 为什么要做

在后台身份门禁、审计读取和用户查询基线建立后，`admin-audit-part1` 才适合补第一批真正的高风险治理动作。本 step 只聚焦用户状态治理本身，让后台具备受控的封禁与解封能力，并把原因与结果纳入权威审计记录。

本批 change 继续沿用 `admin-audit-part1` 作为 series prefix，且 `part1` 仍只覆盖后台入口、审计读取与用户治理最小骨架。当前 step 复用前置 step 的后台身份、审计主线与 `packages/api_contracts` 导出链路，不新增新的 `libs/` 共享层前置 change。

## 本次变更包含什么

- 定义用户封禁与解封的最小状态流转、原因码或备注语义
- 建立受角色约束的治理接口
- 将治理动作写入权威审计记录，确保后续可追溯

## 本次变更不包含什么

- 申诉流程、自动化风控编排或复杂审批流
- 内容级联下线、评论清理或跨模块连带处置
- 后台前端页面实现

## 预期结果

1. 后台具备首批受控的用户状态治理动作。
2. 高风险动作拥有明确的权限校验、原因留痕和结果可追溯能力。
3. 后续 moderation 或运营策略可以复用同一条治理主线继续扩展。

## 影响范围

- `apps/api/src/modules/admin/*`
- `apps/api/src/modules/auth/*`
- `apps/api/src/modules/audit/*`
- `packages/api_contracts/openapi/openapi.json`
