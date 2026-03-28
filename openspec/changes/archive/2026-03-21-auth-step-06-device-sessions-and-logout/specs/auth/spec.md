# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须支持用户治理设备会话并主动退出登录

系统必须允许已登录用户查看自己的设备会话、移除指定设备会话，并主动退出当前登录态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 查看设备会话

- WHEN 已登录用户请求查看设备会话列表
- THEN 系统必须返回该用户当前可管理的设备会话信息

#### Scenario: 移除指定设备会话

- WHEN 已登录用户主动移除某个设备会话
- THEN 系统必须撤销该设备对应的登录态
- AND 被移除设备后续不得继续使用原 refresh token 维持会话

#### Scenario: 主动退出当前设备

- WHEN 已登录用户发起退出当前设备
- THEN 系统必须使当前会话失效
- AND 当前设备后续不得继续使用原登录态访问受保护接口
