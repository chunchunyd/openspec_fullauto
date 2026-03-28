# Delta for Content

## ADDED Requirements

### Requirement: 系统必须为 feed 提供稳定游标化的公开帖子列表

系统必须为 feed 提供稳定游标化的公开帖子列表，并清晰限定该列表只输出满足公开消费条件的帖子卡片结果。 The system MUST provide a stable cursor-based public post list for feed consumption.

#### Scenario: 请求公开帖子列表

- WHEN 上层 feed 或等价消费方请求公开帖子列表
- THEN 系统必须返回只包含公开可消费帖子的稳定分页结果
- AND 结果必须包含卡片渲染所需的最小字段集合

#### Scenario: 连续分页读取公开帖子

- WHEN 调用方使用上一页返回的游标继续请求后续内容
- THEN 系统必须按稳定排序返回下一批结果
- AND 不得因为游标语义含糊导致明显重复、跳项或乱序

