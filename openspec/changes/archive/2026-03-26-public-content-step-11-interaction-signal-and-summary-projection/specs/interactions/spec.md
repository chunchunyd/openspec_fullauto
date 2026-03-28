# Delta for Interactions

## ADDED Requirements

### Requirement: 系统必须把互动动作投影为最小摘要与结构化信号

系统必须把首期互动动作投影为最小互动摘要与结构化行为信号，以便详情页、feed 和后续分析链路消费一致结果。 The system MUST project supported interaction actions into minimal summaries and structured signals.

#### Scenario: 读取帖子互动摘要

- WHEN 调用方读取帖子详情或首页卡片结果
- THEN 系统必须返回由已落地互动动作投影出的最小互动摘要
- AND 摘要字段必须足以支撑首期详情与卡片展示

#### Scenario: 用户完成一次受支持互动动作

- WHEN 用户完成点赞、收藏、评论、关注或举报等受支持互动动作
- THEN 系统必须沉淀一条最小结构化行为信号
- AND 该信号必须能够关联用户、对象和动作类型

