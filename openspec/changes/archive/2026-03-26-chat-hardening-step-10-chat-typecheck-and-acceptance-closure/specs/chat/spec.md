# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须在 chat 发送与重试响应中返回稳定的任务跟踪元数据

系统必须在 owner-scoped private chat 的发送、重试和等价成功响应中返回稳定的任务跟踪元数据，以便调用方能够直接基于首包或重试结果继续追踪同一条任务主线。 The system MUST expose stable task-tracking metadata in chat send and retry success responses.

#### Scenario: 发送消息后返回任务跟踪字段

- **WHEN** 已登录 owner 成功发起一条 private chat 消息，或请求已落入受控的即时失败态
- **THEN** 系统返回的成功响应必须包含平台 task 标识以及当前可用的任务跟踪字段
- **AND** 调用方不得被迫通过额外源码推断才能确认 `runtimeTaskId`、失败信息或等价追踪字段是否存在

#### Scenario: 重试失败消息后返回任务关联信息

- **WHEN** 已登录 owner 对一条失败消息发起手动重试并成功进入新的任务主线
- **THEN** 系统返回的重试响应必须能够表达新任务与原失败任务之间的追踪关联
- **AND** 该关联不得仅停留在服务内部类型，而不进入正式响应契约
