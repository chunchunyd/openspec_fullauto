# 变更提案：Agents Step 05 策略 Metadata 与成熟度读模型

## 为什么要做

Agent 基础资料和读取边界稳定后，下一层最值得单独收敛的是平台侧策略 metadata 与成熟度表达。

如果没有这一步：

- 角色边界、禁区和风格偏好会被随手塞进 profile 字段或运行时配置里
- 公开申请前缺少稳定的成熟度读模型作为前置判断
- 后续 runtime 或 admin 很难围绕统一的 Agent 管理元数据协作

因此需要把策略 metadata 与成熟度读模型单独拆成一个 step，而不是继续把它们混进公开申请或知识/记忆改动里。

## 本次变更包含什么

本次变更聚焦平台侧策略 metadata 与成熟度读模型，范围包括：

- 为 Agent 建立最小策略 metadata 持久化与 owner-scoped 更新边界
- 为 Agent 建立成熟度字段或等价读模型锚点
- 在管理详情中返回当前策略与成熟度结果
- 为后续公开申请和 runtime 消费保留统一读取入口

## 本次变更不包含什么

本次变更不包含以下内容：

- 公开申请提交或审核决定
- 文本知识和分层记忆管理
- runtime prompt 编排或模型路由
- chat、content 的业务接线

## 预期结果

完成后，项目应具备以下结果：

1. 策略 metadata 不再散落在模糊 profile 字段或运行时私有配置中
2. Agent 成熟度有稳定的 API 读模型锚点
3. 后续公开申请与 runtime 消费可以围绕同一份平台侧元数据继续扩展

## 影响范围

本次变更主要影响：

- `prisma/schema.prisma`
- `prisma/migrations/*`
- `apps/api/src/modules/agents/*`
- `apps/api/test` 或 `apps/api/src/modules/agents/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`

