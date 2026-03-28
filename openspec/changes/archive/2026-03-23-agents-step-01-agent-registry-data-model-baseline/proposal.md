# 变更提案：Agents Step 01 Agent Registry 数据模型基线

## 为什么要做

`apps/api` 中的 `agents` 模块目前仍是空壳，但后续 `chat`、`content`、公开 AI IP 和知识/记忆管理都需要一个稳定的 Agent 主数据锚点。

如果继续跳过这一步，后续各能力很容易各自维护 owner、type、visibility 和公开状态，最终形成：

- 不同模块对 Agent 主键和归属关系理解不一致
- chat 或 content 提前耦合还未稳定的 Agent 基础资料结构
- 后续 public read、公开申请和知识/记忆子能力缺少统一持久化入口

因此需要先把 Agent registry 的最小数据模型、仓储边界和 API 模块落位打稳，再继续往上叠加 CRUD 和公开能力。

## 本次变更包含什么

本次变更聚焦 Agent registry 基线，范围包括：

- 为 Agent 主数据建立最小 Prisma 模型与枚举
- 为 owner、type、visibility、public status 和基础资料锚点建立持久化结构
- 在 `apps/api` 中建立 `agents` 模块的 repository / service 基线落位
- 为后续 step 明确与 `users`、`chat`、`content` 的依赖边界

## 本次变更不包含什么

本次变更不包含以下内容：

- Agent 创建、列表、详情或更新接口
- public read 接口
- 策略 metadata、成熟度计算或公开申请流程
- 文本知识和分层记忆管理
- 与 runtime task、chat、content 的业务接线

## 预期结果

完成后，项目应具备以下结果：

1. `agents` 模块不再只有空 `Module`，而是拥有可继续扩展的主数据锚点
2. Agent 的 owner、type、visibility 和公开状态有单一持久化来源
3. 后续 step 可以围绕同一数据模型继续接 CRUD、public 和知识/记忆子能力

## 影响范围

本次变更主要影响：

- `prisma/schema.prisma`
- `prisma/migrations/*`
- `apps/api/src/modules/agents/*`
- `apps/api/test` 或 `apps/api/src/modules/agents/__tests__/*`
- `apps/api/README.md`

