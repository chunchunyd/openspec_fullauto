# Delta for Agents

## ADDED Requirements

### Requirement: 系统必须支持 Agent 文本知识条目的受控管理

系统必须支持 Agent 文本知识条目的受控管理，以避免知识长期混入 profile 文本或其他不可追踪字段。 The system MUST support controlled management of text knowledge entries for an agent.

#### Scenario: 新增文本知识条目

- WHEN Agent owner 为某个 Agent 提交一段合法文本知识
- THEN 系统必须保存该知识条目
- AND 该条目必须能够在后续被 owner 查询和管理

#### Scenario: 修改或删除知识条目

- WHEN Agent owner 修改或删除既有知识条目
- THEN 系统必须返回反映最新状态的受控结果
- AND 非 owner 不得管理该 Agent 的私有知识条目

