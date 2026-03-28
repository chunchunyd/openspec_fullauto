# 变更提案：Public Content Step 04 默认能量场读取模型

## 为什么要做

当前仓库还没有独立 `feed` 模块，首页能量场也没有正式读取边界。仅有 `content` 输出公开帖子列表还不够，客户端仍缺少一个“进入首页就能拿到默认能量场结果”的正式入口。

## 本次变更包含什么

- 在 `apps/api` 建立最小 `feed` 模块与首页读取入口
- 基于 `content` 已加固的公开列表，为首页返回默认 Agent 视角的第一页结果
- 明确 `feed` 复用 `content` 输出，而不是复制帖子查询逻辑

## 本次变更不包含什么

- Agent 切换器
- 刷新、分页与混排策略细化
- 互动写入与互动摘要聚合

## 预期结果

1. 首页能量场拥有正式 API 读取入口。
2. `feed` 与 `content` 的边界从“直接调帖子列表”提升为正式模块协作。
3. 后续 Agent 切换与混排能力有了可持续扩展的入口。

## 影响范围

- `apps/api/src/modules/feed/*`
- `apps/api/src/app.module.ts`
- `apps/api/src/modules/content/*`
- `packages/api_contracts/openapi/openapi.json`

