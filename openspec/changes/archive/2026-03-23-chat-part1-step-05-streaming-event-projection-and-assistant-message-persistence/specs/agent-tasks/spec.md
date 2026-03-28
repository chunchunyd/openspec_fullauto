# Delta for Agent Tasks

## ADDED Requirements

### Requirement: 系统必须为 chat 回复过程保留 append-only 任务事件锚点或等价受控投影

系统必须为 chat 回复过程保留 append-only 任务事件锚点或等价受控投影，以便平台能够围绕统一 task 主线回放流式过程和最终结果。 The system MUST retain an append-only task event anchor or equivalent controlled projection for chat reply execution.

#### Scenario: 聊天任务产生流式事件

- WHEN 一次聊天任务在执行过程中产生渐进式回复事件
- THEN 系统必须能够围绕统一 task 记录这些事件或其等价受控投影
- AND 平台后续必须能够基于这些结果构建 chat 流式读取能力

#### Scenario: 读取聊天任务事件结果

- WHEN 平台需要读取某条聊天用户消息对应的执行过程
- THEN 系统必须能够通过统一 task 主线定位相关事件结果
- AND 调用方不应直接依赖 runtime 私有事件存储作为唯一读取来源
