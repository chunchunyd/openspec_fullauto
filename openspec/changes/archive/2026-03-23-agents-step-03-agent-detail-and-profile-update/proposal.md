# 变更提案：Agents Step 03 Agent 详情与资料更新

## 为什么要做

在用户能够创建并看到“我的 Agent 列表”之后，下一步最自然的闭环就是读取单个 Agent 详情并更新基础资料。

如果没有这一步：

- 列表入口只能看到摘要，无法进入明确的管理详情页
- 后续策略 metadata、知识和记忆能力缺少稳定的详情宿主
- `agents` 模块仍然无法承担最基本的注册管理职责

因此应把 owner-scoped 详情与资料更新单独拆为一个小 step，而不是和 public read 或策略配置混成更大的管理 change。

## 本次变更包含什么

本次变更聚焦 owner-scoped 详情与基础资料更新，范围包括：

- 为已登录 owner 提供单个 Agent 详情读取接口
- 为已登录 owner 提供最小基础资料更新接口
- 约束可更新字段范围，例如名称、头像、角色设定和人格描述
- 为不存在或越权的 Agent 返回受控结果

## 本次变更不包含什么

本次变更不包含以下内容：

- public read 接口
- 策略 metadata、成熟度和公开申请
- 文本知识和分层记忆管理
- 与 chat、content、runtime 的业务接线

## 预期结果

完成后，项目应具备以下结果：

1. owner 可以稳定读取并更新自己的 Agent 基础资料
2. `agents` 模块拥有真实的管理详情宿主，而不是只停留在列表层
3. 后续 public、知识、记忆和策略子能力可以围绕统一详情模型继续展开

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/agents/*`
- `apps/api/test` 或 `apps/api/src/modules/agents/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`

