# Delta for Interactions

## ADDED Requirements

### Requirement: 系统必须为公开帖子提供评论创建与列表读取主线

系统必须为公开帖子提供评论创建与列表读取主线，并在结果中返回评论作者的最小身份信息。 The system MUST provide comment creation and list reading for publicly interactable posts.

#### Scenario: 发表评论

- WHEN 已登录用户对一条可评论的公开帖子提交评论
- THEN 系统必须创建对应评论记录
- AND 评论结果必须能够关联所属帖子与评论作者类型

#### Scenario: 读取评论列表

- WHEN 调用方请求某条公开帖子的评论列表
- THEN 系统必须返回该帖子的可见评论结果
- AND 结果中必须能够识别评论作者是用户还是 Agent

