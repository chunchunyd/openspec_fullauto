# Delta for Analytics

## ADDED Requirements

### Requirement: 系统必须以受控语义处理重复的分析事件写入

系统必须以受控语义处理重复的分析事件写入，以避免把 duplicate conflict 误判成真实存储故障。 The system MUST classify duplicate analytics event writes as controlled duplicate outcomes.

#### Scenario: 并发写入同一 eventId

- WHEN 两个或多个写入同时提交同一个 `eventId`
- THEN 系统必须返回 duplicate 拒绝或等价受控结果
- AND 不得把该冲突误分类为基础设施存储故障

#### Scenario: 非阻塞 emitter 遇到 duplicate conflict

- WHEN 服务端非阻塞 emitter 命中 duplicate conflict
- THEN 系统必须返回 duplicate 语义的结构化结果
- AND 主业务流程仍必须继续执行
