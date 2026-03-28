# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须让 chat 接口接受平台侧 cuid 标识

系统必须让 chat 相关读取、事件和重试接口接受平台侧 `cuid` 标识，并与 Prisma 主键真相源保持一致。 The system MUST accept platform cuid identifiers in chat API contracts instead of enforcing UUID-only input.

#### Scenario: 使用会话 cuid 读取历史消息

- WHEN 客户端携带一个合法的会话 `cuid` 请求历史消息
- THEN 系统必须允许该请求通过参数校验
- AND 不得在控制器层把该请求误判为非法 UUID

#### Scenario: 使用任务或消息 cuid 读取后续结果

- WHEN 客户端携带一个合法的任务 `cuid` 或消息 `cuid` 请求事件或重试
- THEN 系统必须进入真实的业务校验与权限判断
- AND 不得因为平台主键格式与 DTO 约束不一致而提前返回错误

