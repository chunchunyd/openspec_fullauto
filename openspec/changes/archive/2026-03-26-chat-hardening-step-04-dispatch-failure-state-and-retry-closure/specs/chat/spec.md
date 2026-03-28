# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须让 dispatch 失败状态与重试门禁保持一致

系统必须让 chat dispatch bootstrap 失败后的消息状态、任务状态和重试门禁保持一致，避免真实失败消息被卡在不可重试的半断链状态。 The system MUST keep dispatch failure state projection and retry eligibility consistent for chat messages.

#### Scenario: dispatch bootstrap 失败

- WHEN 平台在持久化用户消息和创建任务后，runtime dispatch bootstrap 失败
- THEN 系统必须把该结果投影为受控的失败消息与失败任务状态
- AND 客户端后续读取历史时必须能够识别该失败结果

#### Scenario: 用户重试真实失败消息

- WHEN 用户对一条因 dispatch 或执行失败而进入可重试状态的消息发起手动重试
- THEN 系统必须允许其进入新的受控任务主线
- AND 不得因为旧的消息状态投影不一致而错误拒绝该重试请求

