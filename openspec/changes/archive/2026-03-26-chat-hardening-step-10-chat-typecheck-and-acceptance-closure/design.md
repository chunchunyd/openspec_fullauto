## Context

`chat-hardening` 在 step-05 到 step-09 期间逐步扩展了 send / retry / task-events 的任务跟踪字段与错误语义，但验收 rerun 暴露出验收链本身没有完全跟上：

- 一些 success envelope 仍使用 `success = true/false` 这类属性默认值写法，导致导出的 OpenAPI schema 把布尔标量退化成对象
- chat 相关测试桩没有完整体现 `AgentTaskInfo` 新增的 `runtimeTaskId` / `parentTaskId` 等字段，branch-local TSC 会因此报错

这说明运行时行为与共享契约、测试夹具和类型校验链之间还没有形成稳定闭环。

## Goals / Non-Goals

**Goals:**

- 保证 chat 成功响应的标量字段在 DTO 与共享契约中保持正确类型
- 让 send / retry / task-events 的 task metadata 字段在 DTO、OpenAPI 和 acceptance 测试里保持同一真相
- 让 chat-hardening 的 rerun 验收可以把 chat 本地问题和仓库基线问题分开识别

**Non-Goals:**

- 不改动新的 runtime 行为或 task-events 受控错误承载方式
- 不承接整个 `apps/api` 或 monorepo 的历史类型债务清理
- 不新增前端消费层、SDK 层或新的 API 范围

## Decisions

### 1. 用显式 DTO 标量声明替代依赖属性默认值的导出写法

本 step 会让 chat 相关 success envelope 的布尔字段和 task metadata 字段采用更明确的 DTO / Swagger 声明方式，避免共享 OpenAPI 把布尔字段导成 `type: object`。

不采用“导出后手工修 JSON”方案，因为 API 真相源必须仍然留在 `apps/api` 的 DTO 与控制器定义里。

### 2. 把 chat 相关测试桩视为验收链的一部分，而不是可随意漂移的临时 mock

本 step 会统一更新 chat 相关测试桩、fixture builder 或等价辅助方法，让它们与当前 `AgentTaskInfo` / `TaskInfoDto` 形状一致。

不继续容忍依赖 `as any` 或局部缺字段断言掩盖 drift，因为这会让 rerun 验收失去发现本地回归的能力。

### 3. 验收结果要显式区分 chat-local 问题与仓库基线问题

本 step 的验证会继续执行 chat-hardening 相关 Jest、`openapi-export` 和 TypeScript 检查，并在任务说明或配套说明里明确区分：

- 当前 step 直接引入或修复的问题
- 仓库其他模块现存的基线债务

## Risks / Trade-offs

- [全量 `apps/api` TypeScript 仍可能因为基线债务不绿] → 本 step 至少清掉 chat-local 新问题，并把剩余基线问题显式记录
- [DTO 声明调整可能影响已生成 client] → 在同一 step 内重新导出 OpenAPI 并核对 chat 响应 schema
- [测试桩统一后会暴露更多隐藏 drift] → 这是目标的一部分，优先让 acceptance 链真实反映当前契约

## Migration Plan

本 step 不涉及数据库迁移。部署重点是先对齐 DTO / 测试 / OpenAPI 导出源，再执行 rerun 验收，确保共享契约与本地验证链一起收口。

## Open Questions

- 当前没有额外开放问题；若实现中发现某些 success envelope 需要统一提取基类，也应限制在 chat 响应范围内，不扩成全仓库 DTO 重构。
