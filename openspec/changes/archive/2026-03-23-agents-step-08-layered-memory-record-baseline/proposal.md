# 变更提案：Agents Step 08 分层记忆记录基线

## 为什么要做

与知识条目不同，记忆记录更强调层级和生命周期。如果继续把它和知识条目混成一个 change，很容易把“长期可编辑知识”和“可过期、可归档的记忆”写成同一种东西。

因此需要把分层记忆记录单独拆出来，先建立平台侧记忆锚点和最小管理边界，再考虑 runtime 写入、摘要生成和自动清理。

## 本次变更包含什么

本次变更聚焦分层记忆记录基线，范围包括：

- 为 Agent 建立分层记忆记录的最小持久化模型
- 区分长期画像、长期设定、会话摘要和任务级临时记忆等层级
- 建立 owner 或平台侧受控的记忆读取与最小写入边界
- 为后续 runtime 写回、过期和归档保留生命周期锚点

## 本次变更不包含什么

本次变更不包含以下内容：

- runtime 自动写回记忆
- 摘要生成、裁剪或检索策略
- 知识条目管理
- chat / content 的任务接线

## 预期结果

完成后，项目应具备以下结果：

1. Agent 记忆不再只能依赖 runtime 内存或长上下文拼装
2. 不同记忆层有受控的数据模型和生命周期锚点
3. 后续 runtime、chat 和任务系统可以围绕统一记忆锚点继续扩展

## 影响范围

本次变更主要影响：

- `prisma/schema.prisma`
- `prisma/migrations/*`
- `apps/api/src/modules/agents/*`
- `apps/api/test` 或 `apps/api/src/modules/agents/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`

