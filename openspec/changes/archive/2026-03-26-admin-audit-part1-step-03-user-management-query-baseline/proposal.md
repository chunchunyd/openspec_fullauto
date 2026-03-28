# 变更提案：Admin Audit Part1 Step 03 用户管理查询基线

## 为什么要做

后台用户治理能力要想低风险启动，最先需要的不是复杂处置流，而是受控的用户查询与基础详情读取。作为 `admin-audit-part1` 的并行 step，本次只补齐用户管理列表、搜索和基础详情边界，避免后续治理动作建立在“看不清对象”的前提下。

本批 change 继续沿用 `admin-audit-part1` 作为 series prefix，且 `part1` 仍只覆盖后台入口、审计读取与用户治理最小骨架。当前 step 复用现有 `auth`、`agreements`、潜在 `users` 资料宿主与 `packages/api_contracts` 导出链路，不新增新的 `libs/` 共享层前置 change。

## 本次变更包含什么

- 提供后台用户列表、搜索、筛选、分页和基础详情读取边界
- 复用现有 `auth`、`users`、`agreements` 等事实源中的最小可读字段
- 明确后台可读信息范围与对象不存在时的受控返回

## 本次变更不包含什么

- 用户封禁、解封或其他治理动作
- 复杂风险画像、申诉流或内容级联排查
- 后台前端页面实现

## 预期结果

1. 后台可以稳定检索用户并查看基础详情。
2. 用户治理动作拥有正式的对象选择与详情读取前置能力。
3. 用户管理读取不会提前演化成复杂画像系统。

## 影响范围

- `apps/api/src/modules/admin/*`
- `apps/api/src/modules/auth/*`
- `apps/api/src/modules/users/*`
- `apps/api/src/modules/agreements/*`
- `packages/api_contracts/openapi/openapi.json`
