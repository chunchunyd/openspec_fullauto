# 设计说明：Users Part1 Step 06 共享 OpenAPI 契约与验收收口

## Context

`users-part1` 当前已经有 self profile / settings 的代码主线，但上一轮验收暴露出共享 OpenAPI 产物尚未覆盖 `/users/me` 与 `/users/me/settings`。在项目当前的协作模式下，`packages/api_contracts/openapi/openapi.json` 是前端、生成链路与联调共同读取的共享派生产物，因此需要一个专门的 closure step 把 users 当前接口正式导出并完成最终验收。

这一步建立在前面的两类收口之后：

- step-04：先让数据库 schema 与 migration 历史一致
- step-05：再让 users 自我写入接口的请求校验与错误语义稳定

## Goals / Non-Goals

**Goals:**

- 让共享 OpenAPI 产物正式覆盖 `/users/me` 与 `/users/me/settings`
- 确保导出结果包含代表性的成功、未认证与请求校验失败语义
- 为 `users-part1` 形成一轮清晰的契约与验收收口结果

**Non-Goals:**

- 不新增 users 业务字段或数据库结构
- 不在本 step 内重新设计 users 的请求校验方案
- 不把共享 OpenAPI 产物当作手工维护的真相源

## Decisions

### 1. 以 API 真相源修正导出，而不是手工编辑共享产物

如果导出的 `openapi.json` 缺失路径或代表性响应，修正动作应落在 `apps/api` 的 Swagger 注解、DTO 或控制器响应声明上，而不是直接手改 `packages/api_contracts/openapi/openapi.json`。

### 2. 将 users 自我接口的代表性响应明确到共享契约

本 step 默认把以下结果视为 users 自我接口需要稳定表达的代表性响应：

- 成功结果
- 未认证结果
- 请求校验失败结果

如仍存在受控业务错误，也应在可导出范围内保持可读表达，避免消费方只能通过源码猜测当前语义。

### 3. 把契约导出与最终验收放在同一步收口

如果只导出契约，不同时做一次 spot check 和相关验收，很容易再次留下“文件变了，但不确定是否真覆盖当前接口”的问题。因此这一步把 `openapi-export`、users 相关验证和导出结果检查放在同一个 closure step 中完成。

## Risks / Trade-offs

- [Risk] Swagger 注解未完整表达 users 自我接口的错误结果，导致导出文件仍然缺语义
  → Mitigation：在导出前先审阅 users 控制器响应注解，并对生成结果做 spot check。

- [Risk] 只看 `openapi.json` 有无路径，不检查代表性响应结构，仍可能留下消费方无法依赖的契约缺口
  → Mitigation：把“成功 / 未认证 / 校验失败”纳入本 step 的显式核对范围。

- [Risk] 把契约同步与新的行为返工混在一起，导致 closure step 再次膨胀
  → Mitigation：本 step 原则上只做导出与验收；若发现新的行为缺口，回到新的 follow-up change 处理。

## Migration Plan

1. 审阅 users 自我接口的 Swagger 注解与 DTO 导出能力。
2. 执行 `openapi-export`，更新共享 OpenAPI 产物。
3. Spot check `/users/me` 与 `/users/me/settings` 的路径与代表性响应结构。
4. 完成本轮 users-part1 验收命令与结果记录。

## Open Questions

- 如果 users 自我接口仍存在“业务错误 vs 校验错误”混合表达，是否需要在本 step 中仅修正导出注解，还是在后续 change 中进一步统一错误模型。
