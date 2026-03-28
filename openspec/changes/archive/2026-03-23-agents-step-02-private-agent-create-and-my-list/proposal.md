# 变更提案：Agents Step 02 私有 Agent 创建与我的列表

## 为什么要做

在 Agent registry 主数据基线建立之后，最先需要落地的是“用户能否拥有自己的私有 Agent”。

如果没有这一步：

- `agents` 模块仍然只有底层模型，没有任何真实用户入口
- 后续详情、更新、知识和记忆管理缺少稳定的 owner-scoped 起点
- `chat` 或 `content` 将无法依赖一个明确存在的“我的 Agent”集合

因此应先把创建私有 Agent 与查看“我的 Agent 列表”拆成独立 step，而不是把详情、更新和 public read 一次塞进同一个 change。

## 本次变更包含什么

本次变更聚焦私有 Agent 创建与 owner-scoped 列表，范围包括：

- 为已登录用户提供创建私有 Agent 的最小接口
- 为已登录用户提供“我的 Agent 列表”接口
- 约束新建 Agent 的默认 visibility 与 public status
- 为列表返回最小基础资料与 owner-scoped 结果

## 本次变更不包含什么

本次变更不包含以下内容：

- 单个 Agent 详情或更新接口
- public read 接口
- 策略 metadata、成熟度或公开申请
- 文本知识和分层记忆接口

## 预期结果

完成后，项目应具备以下结果：

1. 已登录用户可以创建自己的私有 Agent
2. 已登录用户可以稳定查看自己的 Agent 列表
3. 后续详情、更新和知识/记忆能力可以围绕同一 owner-scoped 基线继续扩展

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/agents/*`
- `apps/api/src/common/guards/*` 或现有 auth 注入边界
- `apps/api/test` 或 `apps/api/src/modules/agents/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`

