# 变更提案：Admin Audit Part1 Step 06 用户治理状态机加固

## 为什么要做

`admin-audit-part1` 的验收表明，当前 ban / unban 实现会把 `DEACTIVATED` 用户在解封时直接恢复成 `ACTIVE`，从而越权覆盖其他业务主状态。

这意味着当前后台治理动作虽然已经具备最小审计留痕，但还没有形成真正受控的状态机边界，和 step-04 “避免越权修改其他业务主状态”的目标不一致。

本 step 继续沿用 `admin-audit-part1` 作为 series prefix，只收口用户封禁 / 解封的状态机与恢复语义，不混入后台读取门禁返工、审计查询参数硬化或共享 OpenAPI 导出收口。

## 本次变更包含什么

- 为 ban / unban 建立受控状态机，避免解封时一律写回 `ACTIVE`
- 引入恢复封禁前状态所需的最小持久化锚点或等价恢复依据
- 明确缺少恢复锚点或命中非法状态转换时的受控失败语义

## 本次变更不包含什么

- 申诉流、审批流或复杂风险处置编排
- 用户读取门禁返工
- 审计中心查询 API 的筛选与排序硬化

## 预期结果

1. 后台 ban / unban 不再覆盖 `DEACTIVATED` 等非治理 owner 的主状态。
2. 解封动作能够恢复到受支持的封禁前状态，而不是默认写回 `ACTIVE`。
3. 缺少恢复依据或命中非法状态转换时，系统会返回受控失败，而不是静默制造错误状态。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/admin/admin-user-governance.service.ts`
- 必要时的 `apps/api/src/modules/admin/dto/admin-users.dto.ts`
- `apps/api/src/modules/admin/__tests__/admin-user-governance.controller.integration.spec.ts`

