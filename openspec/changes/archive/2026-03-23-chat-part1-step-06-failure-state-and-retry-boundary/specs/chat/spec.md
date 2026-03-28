# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须为 owner-scoped private chat 提供失败状态与手动重试边界

系统必须为 owner-scoped private chat 提供失败状态与手动重试边界，以避免培养皿主流程在失败场景下停留在不可恢复的模糊状态。 The system MUST provide controlled failure states and manual retry boundaries for owner-scoped private chat.

#### Scenario: private chat 回复失败

- WHEN 一次 private chat 回复因 dispatch 失败、执行失败、超时或等价异常而未成功完成
- THEN 系统必须保留可读的失败状态与最小失败信息
- AND 该失败结果必须仍然能够关联原始用户消息与统一 Agent task

#### Scenario: owner 手动重试失败消息

- WHEN 已登录 owner 对一条可重试的失败消息发起手动重试
- THEN 系统必须重新进入受控的发送与执行主线
- AND 新的执行结果必须能够与原始失败消息保持可追踪关联
