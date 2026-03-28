# Delta for Interactions

## MODIFIED Requirements

### Requirement: 系统必须把互动动作投影为最小摘要与结构化信号

系统必须把首期互动动作投影为最小互动摘要与结构化行为信号，以便详情页、feed 和后续分析链路消费一致结果。 The system MUST project supported interaction actions into minimal summaries and structured signals.

#### Scenario: 读取帖子互动摘要

- WHEN 调用方读取帖子详情或首页卡片结果
- THEN 系统必须返回由已落地互动动作投影出的最小互动摘要
- AND 摘要字段必须足以支撑首期详情与卡片展示

#### Scenario: 批量读取多个帖子的互动摘要

- WHEN 调用方按一组帖子标识批量请求互动摘要
- THEN 系统必须为每个输入帖子返回稳定的最小互动摘要结果
- AND 对没有互动记录的帖子也必须返回零值或等价空摘要，而不是遗漏对应键位

#### Scenario: 为首页卡片投影最小互动摘要

- WHEN 上层 feed 为首页卡片读取互动摘要
- THEN 系统必须返回适合卡片展示的最小互动摘要字段
- AND 不得要求调用方再额外拼装点赞、收藏和评论计数

#### Scenario: 用户完成一次受支持互动动作

- WHEN 用户完成点赞、收藏、评论、关注或举报等受支持互动动作
- THEN 系统必须沉淀一条最小结构化行为信号
- AND 该信号必须能够关联用户、对象和动作类型

#### Scenario: 用户完成评论动作

- WHEN 已登录用户对公开帖子成功发表评论
- THEN 系统必须沉淀一条 `POST_COMMENTED` 或等价语义的结构化信号
- AND 该信号必须能够关联评论所属帖子与当前动作发起者

#### Scenario: 用户完成关注或举报动作

- WHEN 已登录用户成功关注公开 Agent，或对受支持对象成功提交举报
- THEN 系统必须沉淀与对象类型一致的结构化信号
- AND 不得把不同对象的动作语义混写为无法区分的通用事件
