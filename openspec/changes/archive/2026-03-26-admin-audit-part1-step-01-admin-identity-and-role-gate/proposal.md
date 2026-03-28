# 变更提案：Admin Audit Part1 Step 01 后台身份与角色门禁

## 为什么要做

当前 `admin` 模块虽然已经有少量控制器骨架，但后台入口仍缺少稳定的独立身份上下文与角色门禁。作为 `admin-audit-part1` 的起点，本 step 先只把后台入口保护好，避免后续用户管理、审计中心和治理动作在没有统一权限边界的前提下继续堆功能。

本批 change 使用 `admin-audit-part1` 作为 series prefix，且 `part1` 只覆盖后台入口、审计读取与用户治理最小骨架。当前 step 复用现有 `auth` / `admin` 边界与 `packages/api_contracts` 导出链路，不新增新的 `libs/` 共享层前置 change。

## 本次变更包含什么

- 明确后台身份来源、角色分级以及与普通用户登录态的关系
- 为后台接口建立统一 guard、decorator、上下文提取或等价门禁基线
- 提供最小后台身份探测入口或等价受保护接口，用于验证门禁生效

## 本次变更不包含什么

- 后台用户管理列表与详情
- 审计中心读取能力
- 内容治理、运营配置和后台前端接入

## 预期结果

1. 后台接口拥有独立且可复用的权限门禁基线。
2. 普通用户与低权限后台角色无法误入高风险后台能力。
3. 后续 `admin-audit-part1` 的其他 step 可以复用统一身份上下文继续推进。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/admin/*`
- `apps/api/src/modules/auth/*`
- `packages/api_contracts/openapi/openapi.json`
