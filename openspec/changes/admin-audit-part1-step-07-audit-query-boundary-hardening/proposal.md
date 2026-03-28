# 变更提案：Admin Audit Part1 Step 07 审计查询边界加固

## 为什么要做

`admin-audit-part1` 的验收表明，当前后台审计中心查询边界仍有两个关键缺口：

- 同时传入 `startTime` 与 `endTime` 时，时间范围实际只生效后一半条件
- `sortBy` / `sortOrder` 没有做运行时白名单校验，非法入参会继续落到 Prisma 动态 `orderBy`

这意味着 step-02 虽然已经建立了最小审计读取入口，但查询边界仍不够受控，和“受控查询、分页与排序”的交付目标不完全一致。

本 step 继续沿用 `admin-audit-part1` 作为 series prefix，只收口后台审计中心查询参数与时间范围硬化，不混入用户读取门禁返工、用户治理状态机修正或共享 OpenAPI 导出收口。

## 本次变更包含什么

- 修正审计日志时间范围条件的组合方式，确保 `startTime + endTime` 能同时生效
- 为 `sortBy` / `sortOrder` 建立显式白名单与字段映射，避免非法参数直接进入 Prisma
- 补充后台审计中心的参数校验与查询组合回归测试

## 本次变更不包含什么

- 新的审计记录类型
- 审计 metadata 暴露策略变更
- 共享 OpenAPI 导出与 admin 系列最终验收收口

## 预期结果

1. 后台审计中心在同时传入开始和结束时间时，会返回真实的时间区间结果。
2. 非法排序字段和非法排序方向会在受控校验层被拒绝，而不是在仓储层或 Prisma 运行时暴露为 500。
3. step-02 的查询边界语义完成硬化，可作为后续验收与导出的稳定基础。

## 影响范围

- `apps/api/src/modules/admin/dto/admin-audit.dto.ts`
- `apps/api/src/modules/audit/audit-log.repository.ts`
- 必要时的 `apps/api/src/modules/audit/audit-log.service.ts`
- `apps/api/src/modules/admin/__tests__/admin-audit.controller.integration.spec.ts`

