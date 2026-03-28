# 变更提案：Agents Step 07 文本知识条目管理

## 为什么要做

Agent 基础管理能力稳定之后，首个最适合独立落地的长期管理资产是文本知识条目。

如果不把它单独拆出来：

- 知识录入会被混进 profile、策略或 memory 字段里，难以管理生命周期
- runtime 消费前缺少平台侧受控的知识真相源
- 后续知识修改、删除和处理状态追踪都无法稳定实现

因此应把“文本知识 CRUD 与处理状态”单独做成一个小 step，而不是和记忆层或公开流程一起混做。

## 本次变更包含什么

本次变更聚焦文本知识条目管理，范围包括：

- 为 Agent 建立文本知识条目与处理状态的持久化锚点
- 为 owner 提供知识条目的新增、列表、详情、更新和删除边界
- 返回最小处理状态或等价元数据，供后续 runtime / indexing 消费

## 本次变更不包含什么

本次变更不包含以下内容：

- 知识切片、向量索引或检索编排
- 分层记忆管理
- 公开申请与审核流

## 预期结果

完成后，项目应具备以下结果：

1. owner 可以为 Agent 维护受控的文本知识条目
2. 知识条目具备最小处理状态与管理生命周期
3. 后续 runtime 或索引层可以围绕统一知识锚点继续扩展

## 影响范围

本次变更主要影响：

- `prisma/schema.prisma`
- `prisma/migrations/*`
- `apps/api/src/modules/agents/*`
- `apps/api/test` 或 `apps/api/src/modules/agents/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`

