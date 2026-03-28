# Delta for Admin

## ADDED Requirements

### Requirement: 系统必须支持后台受控查询用户与查看基础详情

系统必须支持后台受控查询用户与查看基础详情，并且只返回当前后台角色允许读取的最小信息范围。 The system MUST support controlled admin user search and basic detail reads.

#### Scenario: 检索用户列表

- WHEN 具备权限的后台用户按条件检索用户
- THEN 系统必须返回符合条件的用户结果
- AND 结果必须支持最小必要的筛选、分页或排序语义

#### Scenario: 查看用户基础详情

- WHEN 具备权限的后台用户查看某个用户的基础详情
- THEN 系统必须返回该对象的最小基础信息与状态快照
- AND 不得暴露超出当前权限范围的受限字段
