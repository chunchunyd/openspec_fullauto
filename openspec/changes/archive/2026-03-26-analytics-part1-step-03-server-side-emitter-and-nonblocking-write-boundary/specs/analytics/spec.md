# Delta for Analytics

## ADDED Requirements

### Requirement: 系统必须通过非阻塞的服务端发射边界记录分析事件

系统必须通过非阻塞的服务端发射边界记录分析事件，并在写入失败时保护主业务流程继续执行。 The system MUST emit server-side analytics events through a non-blocking boundary.

#### Scenario: 服务端流程发射分析事件

- WHEN 一个受支持的服务端业务流程完成关键动作
- THEN 系统必须能够通过统一 emitter 记录相应分析事件
- AND 该事件必须携带最小可追踪上下文

#### Scenario: 分析写入失败

- WHEN analytics 写入或下游存储发生异常
- THEN 系统必须允许主业务流程继续
- AND 系统必须以受控方式记录失败或降级结果
