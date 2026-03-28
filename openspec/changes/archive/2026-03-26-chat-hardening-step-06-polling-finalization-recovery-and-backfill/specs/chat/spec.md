# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须在轮询主线中恢复遗漏的 finalize 与 assistant 消息回填

系统必须让 chat polling 主线在 task 已完成但 assistant 消息尚未落地时能够恢复 finalize 并完成消息回填，而不是把该能力绑定在当前结果页是否刚好命中完成事件。 The system MUST recover missed polling finalization and backfill the assistant message when the task is complete but the message is still absent.

#### Scenario: finalize 首次失败后再次轮询

- WHEN 某次 polling 已经判断 task 完成，但上一次 finalize 或消息落地失败
- THEN 后续再次轮询时系统必须能够进入受控恢复路径并再次尝试补落 assistant 消息
- AND 不得因为之前已经错过完成事件而永久放弃 finalize

#### Scenario: 客户端越过完成事件后恢复轮询

- WHEN 客户端恢复轮询时，`afterSeq` 已经越过最初的完成事件所在页，但 task 实际已经完成
- THEN 系统必须仍然能够识别“task 已完成但消息未落地”的状态
- AND 必须把 assistant 消息补回正式历史主线，而不是只返回一个没有消息落地的完成标记

