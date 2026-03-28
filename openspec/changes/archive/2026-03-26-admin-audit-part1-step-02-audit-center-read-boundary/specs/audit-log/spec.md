# Delta for Audit Log

## ADDED Requirements

### Requirement: 系统必须为后台审计中心提供受控的查询边界

系统必须为后台审计中心提供受控的查询边界，以便在不改变权威审计记录 owner 的前提下查看关键操作留痕。 The system MUST provide a controlled query boundary for the admin audit center.

#### Scenario: 查询审计记录

- WHEN 具备权限的后台用户按条件查询审计记录
- THEN 系统必须返回符合条件的记录结果
- AND 结果必须保留最小可追溯上下文

#### Scenario: 无权限访问审计中心

- WHEN 不具备相应权限的请求访问审计中心读取边界
- THEN 系统必须拒绝该访问
- AND 不得暴露受限审计字段或原始记录细节
