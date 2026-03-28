# 变更提案：Agents Step 06 公开申请提交与状态读取

## 为什么要做

在 public read 边界、策略 metadata 和成熟度读模型建立之后，`agents` 模块下一个清晰的用户主流程就是“从私有 Agent 发起公开申请”。

如果没有这一步：

- Agent 公开化仍停留在口头流程，没有正式申请入口
- `admin` 或 `moderation` 后续无法围绕稳定申请记录继续接审核能力
- 用户看不到自己的 Agent 当前是否已经处于申请中、被拒绝或等待补充条件

因此需要先把“提交申请与读取申请状态”拆成独立 step，而不是在同一个 change 里把审核决定也一并塞进去。

## 本次变更包含什么

本次变更聚焦公开申请提交与状态读取，范围包括：

- 建立 Agent 公开申请的最小持久化锚点或等价状态记录
- 为 owner 提供提交公开申请接口
- 为 owner 提供当前公开申请状态读取结果
- 明确申请条件至少依赖 owner、visibility / public status 和成熟度前置约束

## 本次变更不包含什么

本次变更不包含以下内容：

- admin 或 moderation 的审批通过 / 驳回接口
- 公开内容发布、feed 曝光或推荐策略
- 文本知识和分层记忆管理

## 预期结果

完成后，项目应具备以下结果：

1. owner 可以正式提交 Agent 公开申请
2. `agents` 模块能返回申请中或等价状态结果
3. 后续 admin / moderation 可以在稳定申请锚点上继续实现审核决定

## 影响范围

本次变更主要影响：

- `prisma/schema.prisma`
- `prisma/migrations/*`
- `apps/api/src/modules/agents/*`
- `apps/api/test` 或 `apps/api/src/modules/agents/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`

