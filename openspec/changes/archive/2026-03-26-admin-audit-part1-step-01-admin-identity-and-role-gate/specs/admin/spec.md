# Delta for Admin

## ADDED Requirements

### Requirement: 系统必须通过独立后台身份上下文与角色门禁保护后台入口

系统必须通过独立后台身份上下文与角色门禁保护后台入口，而不是默认复用普通用户消费侧权限。 The system MUST protect the admin entry with a dedicated admin identity context and role gate.

#### Scenario: 后台用户进入管理入口

- WHEN 一个具备后台权限的用户访问后台受保护接口
- THEN 系统必须允许其进入相应后台能力范围
- AND 请求上下文必须能够携带后台角色信息

#### Scenario: 非后台或低权限用户访问受保护动作

- WHEN 普通用户或低权限后台角色访问超出授权范围的后台接口
- THEN 系统必须拒绝该访问
- AND 不得把后台门禁责任下推给客户端自行判断
