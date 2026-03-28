# 设计说明：Users Part1 Step 05 自我资料与设置接口请求校验加固

## Context

`users-part1` 前三个 step 已经建立了 self profile 读取、资料更新与 settings 宿主，但当前实现仍存在两个边界缺口：

- `UsersController` 没有复用项目中常见的 `ValidationPipe({ whitelist, forbidNonWhitelisted, transform })`
- `UpdateSettingsRequestDto` 只有 Swagger 元数据，没有真正的运行时校验约束

结果是非法字段、错误类型和未受支持取值的拒绝语义没有真正落在 users 写入边界，既不利于稳定错误返回，也会让持久化层承担本该在入口处完成的校验责任。

## Goals / Non-Goals

**Goals:**

- 在 users 自我资料与设置写入入口建立受控请求校验边界
- 让非白名单字段、错误类型和未受支持取值在进入 service / repository 前被稳定拒绝
- 用 controller 或等价集成测试覆盖这类边界回归

**Non-Goals:**

- 不新增 users 资料字段、设置字段或新的业务能力
- 不修改数据库 schema 与 migration 历史
- 不在本 step 内完成共享 OpenAPI 导出同步

## Decisions

### 1. 复用现有控制器级 ValidationPipe 模式，而不是在 `main.ts` 引入全局新策略

当前仓库已经在 `auth`、`agents`、`content`、`chat` 等模块使用控制器级 `ValidationPipe`。本 step 继续沿用这一模式，把 users 写入边界与现有受控 API 对齐，避免在本轮返工中引入额外的全局副作用。

### 2. 将结构性请求校验前移到 DTO 层，service 只保留真正的业务判断

像布尔类型、枚举值、URL 格式、非白名单字段这类结构性约束，应该由 DTO + ValidationPipe 在入口处完成，而不是继续依赖 service 层手写分支兜底。这样可以把“请求不合法”和“业务条件不满足”清晰分开。

### 3. 用 controller / 集成层测试覆盖 400、401 与局部更新边界

当前 users 只有 service 单测，不足以验证非法请求是否真的在 HTTP 边界被拒绝。本 step 明确补 controller 或等价集成测试，至少覆盖：

- 未登录访问返回 401
- 非白名单字段返回 400
- 错误类型与非法枚举返回 400
- 合法局部更新仍保持既有成功语义

## Risks / Trade-offs

- [Risk] 原先 service 内的 `INVALID_FIELD` 业务错误可能收敛成请求校验失败，导致错误语义变化
  → Mitigation：在本 step 中明确“结构性无效输入前移到请求校验边界”，并在下一步共享 OpenAPI 导出时同步稳定契约表达。

- [Risk] 只补 service 单测而不补 controller / 集成测试，仍然无法证明 HTTP 边界真的拒绝无效输入
  → Mitigation：把 controller 或等价集成测试写成正式交付项，而不是可选补充。

- [Risk] users 控制器与其他模块的 ValidationPipe 配置不一致
  → Mitigation：直接复用仓库现有受控 API 的配置模式，避免再发明一套局部规则。

## Migration Plan

1. 在 `UsersController` 上接入控制器级 `ValidationPipe`。
2. 为 self settings DTO 补齐真实的校验装饰器，必要时同步补充 profile 写入相关注解。
3. 增加 controller / 集成测试，覆盖 users 自我写入边界的主要非法输入场景。
4. 运行 users 相关测试和当前 change 验证命令，确认入口处校验生效。

## Open Questions

- 对于 `language` 这类受控枚举值，本 step 默认将其视为请求校验层约束；如果后续产品需要把部分非法值改成业务层可恢复错误，再通过新的 change 明确调整语义。
