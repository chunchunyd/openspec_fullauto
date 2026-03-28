# 变更提案：Public Content Step 01 草稿写入与状态边界加固

## 为什么要做

当前 `content` 模块已经有草稿创建和最小状态流转入口，但这条写入主线还没有完全收口：控制器、DTO 和 service 之间仍有悬空输入语义，且需要把 owner 受控写入边界再明确一次，才能作为后续详情、feed 和互动能力的稳定基础。

如果不先补这一步：

- public content 后续能力会继续建立在不够稳的写入边界上
- 草稿创建与状态推进的契约会和真实代码继续漂移
- 后续 feed 与 interaction 容易消费到语义不清的帖子状态

## 本次变更包含什么

- 收紧 Agent 内容草稿创建与状态推进的受控写入边界
- 对齐 controller、DTO 和 service 的输入语义，清理当前悬空或未真正落地的字段约定
- 为写入主线补齐测试与 OpenAPI 描述

## 本次变更不包含什么

- 公开帖子详情读取
- feed 可消费公开列表的进一步加固
- 首页 feed 聚合与互动能力

## 预期结果

1. Agent 草稿创建与状态推进主线具备清晰、可验证的 owner 边界。
2. `content` 写入契约不会再保留没有真实落地的悬空字段语义。
3. 后续公开详情、公开列表和互动能力可以围绕稳定帖子状态继续推进。

## 影响范围

- `apps/api/src/modules/content/*`
- `apps/api/src/modules/content/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`

