# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须持久化认证账号状态、授权确认与设备会话主数据

系统必须为认证领域持久化最小可用的账号状态、授权确认和设备会话主数据，以支撑登录判定、协议 gating、refresh token 管理和设备会话治理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应具备以下持久化锚点：

- 账号可用状态
- 必要授权确认记录
- 设备会话记录
- 与 refresh token 撤销或轮换相关的受控持久化信息


#### Scenario: 读取账号状态

- WHEN auth 流程需要判断某个手机号对应账号是否允许继续登录
- THEN 系统必须能够从持久化主数据中读取明确的账号状态

#### Scenario: 读取协议确认状态

- WHEN auth 流程需要判断用户是否已完成必要协议与 AI 告知确认
- THEN 系统必须能够从持久化记录中读取对应确认结果与确认时间

#### Scenario: 建立后续设备会话锚点

- WHEN 后续登录流程需要建立、刷新或撤销设备会话
- THEN 系统必须已经存在可承载该信息的持久化主数据结构
