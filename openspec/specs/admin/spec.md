# Admin Specification

## Purpose

本规格定义“能干”项目首期管理后台能力的当前行为真相源。

首期后台能力聚焦于：

- 后台身份登录与权限分级
- 用户管理
- Agent 管理
- 内容与举报处理
- 运营配置管理
- 数据看板
- 审计中心与关键动作留痕

首期不要求复杂多租户后台、跨组织协同审批或完整 BI 自助分析能力作为当前已交付行为，但系统应保留后续扩展空间。
## Requirements
### Requirement: 系统必须提供独立的后台管理入口

系统必须提供面向运营人员与平台管理员的后台管理入口，并将其与普通用户消费侧能力区分。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

后台入口必须基于独立的后台身份与权限控制，而不是默认复用普通用户权限边界。

#### Scenario: 后台用户进入管理系统

- WHEN 一个具备后台权限的用户进入后台
- THEN 系统必须允许其通过后台身份进入管理能力范围

#### Scenario: 普通用户尝试访问后台

- WHEN 一个不具备后台权限的普通用户尝试访问后台能力
- THEN 系统必须拒绝该访问

### Requirement: 系统必须支持后台权限分级

系统必须支持后台权限分级，以控制不同角色可执行的管理动作范围。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持：

- 运营类权限
- 管理员类权限
- 对高风险动作的更严格权限限制

#### Scenario: 低权限角色访问高风险动作

- WHEN 一个后台低权限角色尝试执行高风险动作
- THEN 系统必须拒绝该动作

#### Scenario: 高权限角色执行受控动作

- WHEN 一个具备相应权限的后台角色执行受控动作
- THEN 系统必须允许其进入对应流程

### Requirement: 系统必须支持用户管理

系统必须支持后台对用户进行查询、查看与基础治理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期用户管理至少应支持：

- 用户检索
- 用户详情查看
- 封禁与解封
- 风险事件查看

#### Scenario: 检索用户

- WHEN 后台用户按条件查询用户
- THEN 系统必须返回符合条件的用户结果

#### Scenario: 封禁用户

- WHEN 具备权限的后台用户对某个用户执行封禁
- THEN 系统必须更新该用户的可用状态
- AND 后续该用户的受限行为必须受到影响

#### Scenario: 解封用户

- WHEN 具备权限的后台用户解除某个用户的封禁状态
- THEN 系统必须更新该用户状态

### Requirement: 系统必须支持 Agent 管理

系统必须支持后台对 Agent 进行检索、查看与治理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期 Agent 管理至少应支持：

- Agent 检索
- Agent 详情与配置查看
- 公开申请审核
- Agent 强制下线
- 异常行为排查

#### Scenario: 查看 Agent 详情

- WHEN 后台用户查看某个 Agent
- THEN 系统必须返回该 Agent 的基础信息、公开状态和必要配置快照

#### Scenario: 审核 Agent 公开申请

- WHEN 后台用户处理 Agent 公开申请
- THEN 系统必须允许其给出通过或拒绝等结果
- AND 审核结果必须影响该 Agent 的公开状态

#### Scenario: 强制下线 Agent

- WHEN 后台用户对某个公开 Agent 执行下线
- THEN 系统必须更新其公开可见状态

### Requirement: 系统必须支持内容与举报管理

系统必须支持后台对公开内容和举报结果进行处理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持：

- 帖子审核
- 评论审核
- 举报列表查看
- 举报处理
- 内容下线或隐藏

#### Scenario: 审核帖子或评论

- WHEN 后台用户处理一个待审核内容对象
- THEN 系统必须允许其完成审核动作
- AND 审核结果必须影响该对象后续状态

#### Scenario: 处理举报

- WHEN 后台用户查看并处理一条举报
- THEN 系统必须允许其记录处理结果
- AND 必要时触发后续治理动作

#### Scenario: 下线问题内容

- WHEN 后台用户判定某条内容需要停止公开展示
- THEN 系统必须支持对该内容执行下线或隐藏动作

### Requirement: 系统必须支持运营配置管理

系统必须支持后台维护首期关键运营配置。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持：

- 兴趣分类与标签体系
- 首页策略与频控规则
- 敏感词或风险规则
- 策略模板与 Prompt 资产元数据管理
- 系统配置与功能开关

这些后台配置用于平台治理、策略管理和 runtime 消费边界控制，但不意味着后台直接承诺内嵌 prompt 编排执行引擎。

#### Scenario: 更新首页策略

- WHEN 后台用户更新首页策略、蓝红能量比例或等价配置
- THEN 系统必须保存新的配置结果
- AND 后续首页输出应能够使用更新后的配置

#### Scenario: 更新风险规则或敏感词

- WHEN 后台用户维护风险规则或敏感词配置
- THEN 系统必须保存新的规则结果

#### Scenario: 管理策略模板元数据

- WHEN 后台用户新增、查看或更新策略模板或 Prompt 资产元数据
- THEN 系统必须支持对应的模板管理动作

### Requirement: 系统必须支持数据看板

系统必须支持后台查看首期核心运营指标。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期数据看板至少应支持查看以下指标中的全部或核心子集：

- 新增
- 留存
- DAU
- 内容产量
- 互动率
- 会话转化率
- 公开 IP 数量
- 违规率

#### Scenario: 查看总览看板

- WHEN 后台用户访问数据看板
- THEN 系统必须返回首期核心指标总览结果

### Requirement: 系统必须支持审计中心

系统必须支持后台查看关键操作日志、审批或审核记录，以及异常告警记录。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 查看关键操作日志

- WHEN 后台用户访问审计中心
- THEN 系统必须返回关键管理动作的日志结果

#### Scenario: 查看异常告警或审批记录

- WHEN 后台用户查看异常告警或相关审批记录
- THEN 系统必须能够返回对应记录结果

### Requirement: 系统必须对高风险后台动作留痕

系统必须对高风险后台动作进行留痕，以支持责任追踪和事后复盘。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖：

- 用户封禁与解封
- Agent 公开审核
- Agent 强制下线
- 内容审核与下线
- 举报处理
- 关键运营配置变更

#### Scenario: 执行高风险后台动作

- WHEN 后台用户执行一个高风险管理动作
- THEN 系统必须记录该动作
- AND 记录中必须能够追溯操作人、目标对象、执行时间和动作结果

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

### Requirement: 系统必须对后台用户状态治理动作执行受控权限校验与原因留痕

系统必须对后台用户状态治理动作执行受控权限校验与原因留痕，并将结果写入可追溯的权威审计记录。 The system MUST enforce controlled permissions and reason capture for admin user status governance actions.

#### Scenario: 后台执行用户封禁或解封

- WHEN 具备相应权限的后台用户对某个用户执行封禁或解封
- THEN 系统必须完成受控状态变更或其等价结果
- AND 系统必须记录该动作的操作人、目标对象、原因和结果

#### Scenario: 低权限角色尝试执行高风险治理动作

- WHEN 低权限后台角色尝试执行用户状态治理动作
- THEN 系统必须拒绝该动作
- AND 不得留下未授权但已生效的状态修改

