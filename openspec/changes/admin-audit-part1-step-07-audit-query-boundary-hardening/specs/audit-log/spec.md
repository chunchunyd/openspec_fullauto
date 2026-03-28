# Delta for Audit Log

## MODIFIED Requirements

### Requirement: 系统必须为后台审计中心提供受控的查询边界

系统必须为后台审计中心提供受控的查询边界，以便在不改变权威审计记录 owner 的前提下查看关键操作留痕。查询边界必须支持可组合的时间区间条件与受控排序字段，而不是让非法参数继续落到底层仓储或数据库动态执行。 The system MUST provide a controlled query boundary for the admin audit center, including composable time-range filters and a controlled set of sortable fields.

#### Scenario: 查询审计记录

- WHEN 具备权限的后台用户按条件查询审计记录
- THEN 系统必须返回符合条件的记录结果
- AND 结果必须保留最小可追溯上下文

#### Scenario: 同时传入开始和结束时间

- WHEN 具备权限的后台用户同时传入开始时间和结束时间查询审计记录
- THEN 系统必须同时应用这两个时间边界
- AND 不得静默丢弃其中任一条件

#### Scenario: 非法排序字段或方向

- WHEN 请求方向后台审计查询边界传入不受支持的排序字段或排序方向
- THEN 系统必须返回受控参数错误
- AND 不得把非法排序参数继续传入底层数据库查询

#### Scenario: 无权限访问审计中心

- WHEN 不具备相应权限的请求访问审计中心读取边界
- THEN 系统必须拒绝该访问
- AND 不得暴露受限审计字段或原始记录细节

