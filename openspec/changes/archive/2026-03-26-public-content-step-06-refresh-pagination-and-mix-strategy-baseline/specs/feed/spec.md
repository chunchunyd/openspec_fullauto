# Delta for Feed

## ADDED Requirements

### Requirement: 系统必须为首页 feed 提供刷新、分页与最小混排策略

系统必须为首页 feed 提供刷新、分页与最小混排策略，并把结果组合控制保留在服务端而不是客户端硬编码。 The system MUST provide refresh, pagination, and a minimal server-controlled mixing strategy for the home feed.

#### Scenario: 下拉刷新或重新请求首页

- WHEN 用户触发首页刷新或重新请求当前 Agent 视角
- THEN 系统必须返回受控的新结果或等价最新结果
- AND 客户端必须能够据此识别空态、异常或可重试状态

#### Scenario: 加载更多首页内容

- WHEN 用户请求当前首页视角的下一页结果
- THEN 系统必须按稳定顺序返回下一批结果
- AND 返回结果的混排顺序必须由服务端策略控制

