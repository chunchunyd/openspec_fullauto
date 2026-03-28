# Delta for Feed

## ADDED Requirements

### Requirement: 系统必须为能量场首页返回受控的 Agent 切换边界

系统必须为能量场首页返回受控的 Agent 切换边界，让客户端能够明确当前选中的 Agent 视角并切换到其他可消费视角。 The system MUST expose a controlled agent-switcher boundary for the home feed.

#### Scenario: 首页返回可切换 Agent 列表

- WHEN 用户请求首页 feed
- THEN 系统必须能够返回当前 feed 可切换的 Agent 摘要集合
- AND 结果中必须能识别当前选中的 Agent 视角

#### Scenario: 切换到另一个 Agent 视角

- WHEN 用户在首页切换到另一个可消费的 Agent
- THEN 系统必须返回该 Agent 视角下的新 feed 结果
- AND 不得继续把上一视角的结果误当作当前数据

