## Context

当前 `admin-users` 读取接口的真实门禁仍然停留在“API key 匹配 + `x-admin-user-id` 非空”这一层，而不是 step-01 已经建立的“后台用户存在、启用、角色满足要求”的受控后台身份主线。

本 step 的目标不是重写整个 admin 鉴权系统，而是把用户读取边界重新接回 step-01 的主线，并让测试同时覆盖“伪造 header 不再可读”这件事。

## Goals / Non-Goals

**Goals**

- 让用户列表与用户详情读取边界复用 `AdminGuard`
- 显式声明读取接口的最低角色要求，而不是依赖隐式默认值
- 让 `admin-users` 相关测试按照新的 guard 依赖图和拒绝语义通过

**Non-Goals**

- 不改动 ban / unban 的状态机
- 不收口审计中心查询的时间范围和排序问题
- 不在本 step 统一替换所有 admin 控制器上的 guard

## Decisions

### 1. 用户读取接口统一回到 `AdminGuard` 主线

本 step 会把 `GET /admin/users` 与 `GET /admin/users/:userId` 统一挂到 `AdminGuard` 上，让请求必须先经过：

- API key 校验
- 后台用户存在性校验
- 后台用户启用状态校验
- 角色分级校验

不再接受“只要 header 不为空就允许读取用户数据”的门禁语义。

### 2. 读取接口显式声明最低角色为 `OPERATOR`

虽然 `AdminGuard` 当前对未标注角色的端点默认使用 `OPERATOR`，但本 step 会在读取接口上显式使用 `@RequireAdminRole(AdminRole.OPERATOR)`，把读取能力的最低权限语义直接暴露在 controller 上。

这样做的目的是让：

- 代码审阅更直接
- 测试更容易针对角色语义建模
- 后续如果默认角色策略变化，读取接口不会静默漂移

### 3. `AdminInternalGuard` 不再作为用户读取的权威门禁

本 step 不要求删除 `AdminInternalGuard`，但会明确：

- 它不能继续作为后台用户读取边界的权威 guard
- 若仍保留在仓库中，只能用于真正的内部桥接场景，而不是用户管理正式入口

## Risks / Trade-offs

- [读取接口将额外查询后台用户主数据] -> 这是 step-01 已经承诺的后台身份成本，换来真实安全边界，代价可接受
- [测试模块需要补齐更多 provider] -> 这是 guard 语义真实收口所必需的成本，优于维持一个已经失真的“伪集成测试”

## Migration Plan

本 step 不涉及 schema 迁移。实施重点是先切换 controller 门禁，再对齐测试装配与拒绝断言。

## Open Questions

- 如果实施时发现 `AdminInternalGuard` 仍被其他正式后台读取路径复用，应记录这些入口，但不要在本 step 顺手扩展到无关控制器。

