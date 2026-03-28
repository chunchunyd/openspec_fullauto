# 设计说明：Users Part1 Step 04 持久化 migration 收口

## Context

`users-part1-step-01-profile-data-model-and-self-read-baseline` 与 `users-part1-step-03-preferences-and-notification-settings-baseline` 已经把 users 资料字段和 `UserSettings` 宿主写进了当前 `prisma/schema.prisma`，但系列验收暴露出这些结构尚未进入正式 migration 历史。

当前问题不在于重新设计 users 数据模型，而在于让仓库重新满足 `repository-structure` spec 中“schema 与已提交 migration 历史保持同步”的交付基线。

## Goals / Non-Goals

**Goals:**

- 以当前 `prisma/schema.prisma` 为目标状态补齐 users-part1 相关 migration 历史
- 让 `User` 的资料字段与 `UserSettings` 宿主能够被新环境通过 migration 正确重建
- 用 drift 校验和 Prisma client 生成链路证明这次收口有效

**Non-Goals:**

- 不新增资料字段、设置字段或额外 users 业务能力
- 不修改 `GET/PATCH /users/me*` 的控制器行为与请求校验策略
- 不在本 step 内同步共享 OpenAPI 契约

## Decisions

### 1. 以当前 schema 为目标状态补齐 migration，而不是回退 schema

这一步的目标是让 migration 历史追上当前 users-part1 已经进入主线的结构，而不是回退 `prisma/schema.prisma` 再重新拆字段。这样可以避免把已归档 step 的能力重新打散，也更符合本 step 的“closure”语义。

### 2. 采用补齐式 migration，不重写既有历史

本 step 默认保留当前 migration 历史不动，只新增有边界的 migration 来覆盖 users-part1 已经进入 schema 的结构。这样可以避免改写既有历史带来的额外风险，也便于后续审查这次回补的具体内容。

### 3. 用 drift 校验而不是“文件已存在”判定收口

仅仅生成 migration 文件不足以证明收口完成；验收必须至少包含：

- `prisma migrate diff` 或等价 drift 校验为空
- `pnpm db-generate` 或等价 Prisma client 生成链路可用

必要时再补一次基于 migration 的空库初始化验证，确认新环境可以只靠已提交历史重建 users-part1 数据结构。

## Risks / Trade-offs

- [Risk] 回补 migration 时把未计划的新 schema 漂移一起夹带进去
  → Mitigation：先明确只覆盖 `nickname`、`avatar`、`bio`、`user_settings` 及其直接约束，再审查 migration diff。

- [Risk] 只补 migration 文件，不做 drift 校验，仍留下 enum / index / foreign key 级别漂移
  → Mitigation：把 drift 校验和 Prisma client 生成都写成正式验收项。

- [Risk] 新 migration 依赖“当前数据库为空”的隐式环境假设
  → Mitigation：在说明里明确采用补齐式 migration 的前提，并尽量以新环境可重建为目标做验证。

## Migration Plan

1. 审阅当前 `prisma/schema.prisma` 中 users-part1 已进入主线的结构。
2. 生成覆盖这些结构的正式 migration。
3. 运行 drift 校验，确认 schema 与 migration 历史一致。
4. 运行 `pnpm db-generate` 或等价验证，确认 Prisma client 生成链路可用。

## Open Questions

- 如果本地开发数据库中已经存在手工对齐后的结构，是否需要额外保留一次“全新数据库只跑 migration”的验证记录，作为后续收口说明的一部分。
