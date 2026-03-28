# 变更提案：Agents Step 04 可见性与 Public Read 边界

## 为什么要做

在 owner-scoped 管理入口稳定之后，接下来最容易失控的就是“谁能读取哪个 Agent”。

如果没有一个单独的 public read 边界 step：

- 私有 Agent 很容易被详情接口或列表接口意外暴露
- 后续 `chat`、`content` 和 feed 消费侧会各自实现一套访问判定
- 公开状态与管理状态会被混成模糊的读权限逻辑

因此需要单独建立可见性与 public read 边界，而不是继续把 owner 管理接口直接扩成“大家都能读”。

## 本次变更包含什么

本次变更聚焦读取边界，范围包括：

- 明确私有管理读取与 public read 的访问判定差异
- 为公开可见 Agent 建立受控的 public read 接口或等价读取边界
- 约束 private / pending / rejected / offline 等状态下的读取结果
- 为后续 chat、content 和 feed 侧复用统一可访问判定

## 本次变更不包含什么

本次变更不包含以下内容：

- owner 侧基础资料更新
- 策略 metadata、成熟度和公开申请提交
- 文本知识和分层记忆管理

## 预期结果

完成后，项目应具备以下结果：

1. private 管理读取与 public read 有明确边界
2. 非 owner 无法误读私有 Agent
3. 后续消费侧可以围绕统一 public read 边界接入，而不需要各自重写可访问判定

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/agents/*`
- `apps/api/test` 或 `apps/api/src/modules/agents/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- `apps/api/README.md`

