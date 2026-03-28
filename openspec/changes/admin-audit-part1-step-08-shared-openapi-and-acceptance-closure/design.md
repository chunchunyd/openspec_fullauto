## Context

`admin-audit-part1` 前几步主要在收口行为缺陷，但验收结果已经说明：如果不再补一轮契约与测试收口，这条 series 仍然会停留在“实现大致可用，但契约与回归链条不稳定”的状态。

本 step 的职责不是再改业务范围，而是把已经承诺的后台路径做成真正可验收、可导出、可继续接入的稳定基线。

## Goals / Non-Goals

**Goals**

- 统一后台用户治理接口的运行时 HTTP 状态码与契约注解
- 修复受 `AdminGuard` 依赖图影响的 admin 集成测试装配
- 刷新共享 OpenAPI 产物并完成 admin 系列最终验收记录

**Non-Goals**

- 不新增新的后台业务接口
- 不继续返工 step-05 到 step-07 的主业务语义
- 不把共享层历史依赖噪音一次性全部清理掉

## Decisions

### 1. 用户治理动作统一以 `200 OK` 表达受控执行结果

本 step 会把 ban / unban 这类“状态改变但不创建新资源”的后台治理动作对齐到 `200 OK`。

原因是：

- 与当前 Swagger 预期一致
- 与后台治理动作的语义更匹配
- 更利于共享 OpenAPI 和消费方保持稳定认知

### 2. 测试模块必须按真实 guard 依赖图装配

`admin-users` 与 `admin-agents` 的测试不再允许停留在旧的 `AdminInternalGuard` 假设上。本 step 会要求测试模块真实补齐：

- `AdminGuard`
- `AdminIdentityService`
- `AdminIdentityRepository` mock
- 必要的 `Reflector` 或等价依赖

目标是让测试失败真正代表行为问题，而不是代表测试装配已经过期。

### 3. 验收收口以“共享契约 + targeted 验收”完成

本 step 不追求在当前仓库把所有全量 typecheck 噪音都清到零，而是要做到：

- admin-audit-part1 已交付接口的共享 OpenAPI 产物已同步
- admin 相关 targeted Jest 验收能够反映真实状态
- 若仍存在 series 范围外共享依赖 blocker，要显式记录，而不是静默跳过

## Risks / Trade-offs

- [状态码从 201 调整到 200 会影响现有断言] -> 这是契约一致性修正，应通过 OpenAPI 和测试同步一次性收口
- [测试装配更接近真实依赖图后，维护成本略升] -> 但这能显著减少“测试文件存在却根本跑不起来”的假覆盖

## Migration Plan

本 step 不涉及 schema 迁移。实施顺序建议是：

1. 先对齐 controller 的 HTTP 状态码与 Swagger 注解
2. 再修正 admin 相关测试装配
3. 最后执行 OpenAPI 导出和 targeted 验收

## Open Questions

- 如果实现时发现某些 admin 接口已经在其他 active change 中继续演进，应只在本 step 记录并协调，不要把 unrelated 接口也顺手纳入收口范围。

