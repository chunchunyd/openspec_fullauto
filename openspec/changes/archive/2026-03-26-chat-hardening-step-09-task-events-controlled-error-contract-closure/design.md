## Context

当前 `chatService.getTaskEvents()` 已经能够区分：

- 平台 task 不存在或越权
- 平台 task 已存在但 `runtimeTaskId` 尚未建立
- runtime 读取过程暂时失败

但 controller 和 DTO 仍只保留 `taskId`、`status`、`events`、`isCompleted` 这些成功页字段，导致 service 中的 `result.error` 无法穿透到 HTTP 契约和 OpenAPI 产物。结果是客户端只能靠 `UNKNOWN` 和空数组猜测真实状态。

## Goals / Non-Goals

**Goals:**

- 保留 task-events 现有成功轮询路径和 404/鉴权边界
- 在 HTTP 契约中明确表达 not-linked / runtime-unavailable 等受控错误语义
- 让 OpenAPI 导出、controller 实际返回和 service 真实语义保持一致

**Non-Goals:**

- 不新增新的 task event 类型或 streaming 协议
- 不改变 finalize 触发逻辑和 send / retry 主线
- 不把该接口改造成新的 push、订阅或长连接协议

## Decisions

### 1. 继续沿用 task 已存在时的 HTTP 200 success envelope，并显式加入受控错误字段

本 step 选择保留现有 polling 读取接口的 200 success envelope，在成功体中加入 `errorCode` / `errorMessage` 或等价字段来表达：

- runtime task 尚未关联
- runtime 暂时不可读

这样可以保持调用方的 polling 模式稳定，不必把“task 已存在但当前未就绪/暂时异常”强行映射成全新的错误状态码。

不采用“把这类情况全部提升成 4xx/5xx”方案，因为调用方读取的是一个已存在、且可能稍后恢复的 task；把它设计成受控成功体更利于前端继续轮询同一任务。

### 2. 差异化语义需要在 service、controller、DTO、OpenAPI 四层同时收口

本 step 会把受控错误字段从 `ChatService` 透传到 controller，并在 DTO 与 OpenAPI 导出中固定下来。只有这样，step-02 已建立的差异化语义才不会再被中间层吞掉。

不接受“service 保留 error，但 controller 继续只返回 UNKNOWN”的折中方案，因为这会继续制造源码与共享契约的双重真相源。

### 3. 明确 normal-empty 与 error-empty 的边界

本 step 会把“当前无新增事件但 task 仍在运行”和“当前没有 events，但因为 runtime 未映射/暂时不可读而无法提供事件”区分开来：

- normal-empty：无错误字段，`status` 和 `isCompleted` 反映真实 task 状态
- error-empty：保留受控错误字段，供调用方做提示、退避或继续重试

## Risks / Trade-offs

- [客户端需要适配新的可选错误字段] → 保持原有 `taskId` / `status` / `events` / `isCompleted` 不变，仅附加可选字段
- [UNKNOWN 状态语义仍然过宽] → 用明确的 `errorCode` / `errorMessage` 收窄实际消费语义
- [OpenAPI 变更影响已生成 client] → 在同一 step 内执行 `openapi-export` 并补齐代表性 contract 测试

## Migration Plan

本 step 不涉及数据库迁移。部署时先更新 API DTO 与 controller，再导出新的 OpenAPI 契约；调用方在未适配新字段前仍可沿用旧字段读取，只是无法消费新增的细粒度错误语义。

## Open Questions

- 当前默认沿用 200 success envelope；若实现时发现前端或现有 client 必须使用不同的错误承载方式，再在本 step 内统一调整，不额外新开系列。
