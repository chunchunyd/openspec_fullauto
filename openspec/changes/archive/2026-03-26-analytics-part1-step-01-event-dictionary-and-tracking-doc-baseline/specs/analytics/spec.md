# Delta for Analytics

## ADDED Requirements

### Requirement: 系统必须维护统一的首期事件字典真相源

系统必须维护统一的首期事件字典真相源，以约束事件命名、属性口径、最小上下文和版本变更规则。 The system MUST maintain a single source of truth for the initial analytics event dictionary.

#### Scenario: 查询事件定义

- WHEN 研发、测试或运营需要确认某个事件的定义
- THEN 系统必须存在统一可引用的事件字典来源
- AND 该来源必须说明事件名称、属性口径和最小上下文要求

#### Scenario: 调整事件口径

- WHEN 一个已有事件或属性口径发生变化
- THEN 系统必须记录该变化
- AND 不得以隐式改名或私下修改方式导致口径失真
