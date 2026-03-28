# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须生成、缓存并发送登录验证码

系统必须支持在登录前为合法手机号生成、缓存并发送一次性验证码，以作为后续身份校验输入。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 请求登录验证码

- WHEN 用户提交合法手机号并请求登录验证码
- THEN 系统必须生成受控的一次性验证码
- AND 系统必须以短期缓存形式保存该验证码
- AND 系统必须通过共享短信发送能力完成发送

### Requirement: 系统必须对验证码发送应用冷却时间与基础发送频控

系统必须对登录验证码发送应用冷却时间与基础发送频控，避免同一手机号或同一请求来源在短时间内重复触发发送。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 冷却期内重复请求

- WHEN 同一手机号仍处于验证码发送冷却期
- THEN 系统不得继续按正常流程重新发送验证码

#### Scenario: 短时间内频繁请求

- WHEN 同一手机号或同一请求来源在短时间内频繁请求验证码
- THEN 系统必须触发基础发送频控
- AND 系统不得继续按正常节奏发送验证码
