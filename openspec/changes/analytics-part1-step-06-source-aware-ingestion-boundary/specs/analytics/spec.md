# Delta for Analytics

## ADDED Requirements

### Requirement: 系统必须保留原始分析事件的来源语义

系统必须保留原始分析事件的来源语义，以区分客户端上报与服务端发射事件。 The system MUST preserve source semantics for raw analytics events.

#### Scenario: 接收客户端原始事件

- WHEN 一个客户端 collector 或等价调用方提交原始分析事件
- THEN 系统必须能够将其来源记录为客户端语义
- AND 不得把该事件静默折叠为服务端事件

#### Scenario: 服务端流程发射事件

- WHEN 一个服务端业务流程通过统一 analytics emitter 发射事件
- THEN 系统必须能够将其来源记录为服务端语义
- AND 业务调用方不应被迫直接拼装 raw ingestion 的底层来源细节
