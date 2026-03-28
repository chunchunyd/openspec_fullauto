# SMS Specification

## Purpose

本规格定义“能干”项目当前共享短信发送能力的行为真相源。

首期短信能力聚焦于：

- 提供统一的共享短信发送抽象
- 支持开发与测试使用的调试替身
- 统一短信发送结果与错误边界

## Requirements

### Requirement: 系统必须提供统一的共享短信发送抽象

系统必须提供统一的共享短信发送抽象，供 `auth` 等业务能力复用，而不是由每个业务模块分别维护独立 provider 接线。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期该共享层至少应包括：

- 统一短信发送 port
- 统一发送请求模型
- 统一发送结果模型


#### Scenario: Auth 触发短信发送

- WHEN `auth` 或其他业务能力需要发送短信
- THEN 它必须通过共享短信发送抽象发起请求
- AND 不应在业务模块内部长期复制独立 provider factory 或供应商接线

### Requirement: 系统必须支持开发与测试使用的短信调试替身

系统必须支持开发与测试使用的短信调试替身，以避免本地开发默认依赖真实短信供应商。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 本地开发发送验证码短信

- WHEN 开发者在本地开发环境中触发短信发送
- THEN 系统必须能够使用受控的 fake 或 debug provider 完成验证
- AND 本地开发流程不应默认要求真实供应商账号和真实发送

#### Scenario: 调试替身输出敏感内容

- WHEN 调试替身需要暴露与验证码或模板参数相关的调试信息
- THEN 它必须遵循环境限制和脱敏规则
- AND 不得把敏感内容作为普通生产日志长期输出

### Requirement: 系统必须统一短信发送错误与结果边界

系统必须统一短信发送结果与错误边界，以避免业务模块直接依赖各供应商的原始响应格式。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: provider 发送成功

- WHEN 共享短信层调用 provider 成功
- THEN 系统必须返回统一的发送结果
- AND 结果中可包含 provider 名称和 provider message id 等受控字段

#### Scenario: provider 发送失败

- WHEN 共享短信层调用 provider 失败或返回异常结果
- THEN 系统必须返回或抛出统一边界下的失败信息
- AND 业务模块不应直接依赖供应商原始错误格式进行长期分支判断
