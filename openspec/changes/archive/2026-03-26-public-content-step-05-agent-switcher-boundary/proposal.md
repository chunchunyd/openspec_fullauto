# 变更提案：Public Content Step 05 Agent 切换器边界

## 为什么要做

首页默认 feed 建立之后，还需要把“多个常用 Agent 之间的能量场切换”落成正式边界。没有切换器，能量场仍停留在单一默认视角，无法支撑需求文档中的常用 Agent 消费入口。

## 本次变更包含什么

- 为首页返回可切换的 Agent 列表与当前选中结果
- 定义切换目标 Agent 后重新读取对应 feed 的受控输入边界
- 明确只允许消费侧切换可见、可用的 Agent 视角

## 本次变更不包含什么

- 复杂混排与排序策略
- 点赞评论等互动结果聚合
- 关注关系写入

## 预期结果

1. 首页 feed 有正式的 Agent 切换边界。
2. 切换输入和结果语义对前后端都更清楚。
3. 后续刷新与分页可以围绕切换后的 feed 主线继续扩展。

## 影响范围

- `apps/api/src/modules/feed/*`
- `apps/api/src/modules/agents/*`
- `packages/api_contracts/openapi/openapi.json`

