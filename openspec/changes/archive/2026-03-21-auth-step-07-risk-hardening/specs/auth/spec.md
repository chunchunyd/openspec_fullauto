# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须记录并判定基础登录风险信号

系统必须在认证流程中记录并判定最小请求来源或设备风险信号，并将其用于基础受控限制或受控拒绝。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 请求来源或设备信号明显异常

- WHEN 登录请求命中受控定义下的异常请求来源或异常设备信号
- THEN 系统必须触发基础风险判定
- AND 系统可以对该请求施加受控限制或受控拒绝

#### Scenario: 记录风险判定上下文

- WHEN auth 流程命中风险限制或风险拒绝分支
- THEN 系统必须记录最小结构化上下文
- AND 日志不得直接泄露验证码、完整手机号或完整 token
