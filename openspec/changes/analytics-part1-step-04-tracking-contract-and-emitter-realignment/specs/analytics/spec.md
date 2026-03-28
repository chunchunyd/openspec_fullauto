# Delta for Analytics

## MODIFIED Requirements

### Requirement: 系统必须维护统一且与实现一致的首期事件字典真相源

系统必须维护统一且与实现一致的首期事件字典真相源，以约束当前已接线服务端事件的名称、关键字段和指标引用口径。 The system MUST keep the initial analytics event dictionary aligned with implemented emitter contracts.

#### Scenario: 当前已接线服务端事件发射

- WHEN `auth`、`agents` 等当前已接线模块发射分析事件
- THEN 事件名称和关键 payload 字段必须与 tracking 字典中的定义一致
- AND 不得同时保留“文档事件名”和“代码事件名”两套并行语义

#### Scenario: 新增或调整稳定事件契约

- WHEN 一个稳定的服务端事件被新增或调整
- THEN 同一 change 必须同步更新事件字典、相关指标说明和 emitter 契约
- AND 不得只修改其中一侧而让 tracking 真相源失效
