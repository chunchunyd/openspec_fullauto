# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须通过轮询主线返回受控完成语义并落地 assistant 消息

系统必须通过当前公开的 chat 轮询主线返回受控完成语义，并在成功完成后落地 assistant 消息，而不是只在内部 stream 路径上完成最终投影。 The system MUST expose controlled completion semantics and finalize assistant messages through the polling path that clients actually use.

#### Scenario: 轮询时当前暂无新事件

- WHEN 客户端轮询某个仍在运行中的 chat 任务且当前页没有新增事件
- THEN 系统必须把该结果表达为“当前无新增”或等价未完成状态
- AND 不得把它误报为任务已经完成

#### Scenario: 轮询确认任务成功完成

- WHEN 客户端轮询到某个 chat 任务已经成功完成
- THEN 系统必须把最终 assistant 回复落地为会话消息
- AND 会话最近消息摘要与最近活跃时间必须随之更新

