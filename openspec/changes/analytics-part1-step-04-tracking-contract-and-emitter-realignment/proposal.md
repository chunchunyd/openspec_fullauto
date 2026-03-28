# 变更提案：Analytics Part1 Step 04 Tracking 契约与 Emitter 对齐收口

## 为什么要做

`analytics-part1` 前三步已经补出了事件字典、原始事件存储锚点和服务端 emitter，但本轮验收发现 `docs/tracking/*` 中的事件名称与指标口径，已经和 `auth`、`agents` 里真实发射的事件名/字段明显漂移。继续在这种状态下往后扩展，会让 step-01 建立的事件字典不再是可信真相源，也会让后续指标聚合直接建立在错误事件名之上。

这一步继续沿用 `analytics-part1` 作为 series prefix，只收口“当前已接线的首批服务端事件契约”与 tracking 文档的一致性，不在这一轮同时补 migration、来源语义或 duplicate 并发语义。

## 本次变更包含什么

- 盘点当前 `auth`、`agents` 已经接入的首批 analytics 服务端事件，确定一套统一的 canonical event name 与关键 payload 字段
- 对齐 `docs/tracking/event-dictionary.md`、`docs/tracking/metrics-definition.md`、`openspec/specs/analytics/spec.md` 与当前 emitter 调用点，消除“文档事件名”和“代码事件名”并存的状态
- 收紧“新增稳定事件时必须同步更新 tracking 真相源”的项目内约束，让后续 step 扩展基于同一份口径继续推进

## 本次变更不包含什么

- `analytics_raw_events` 的 Prisma migration 与 generated client 收口
- 原始事件 `source` 的客户端 / 服务端语义补齐
- duplicate 写入并发冲突的受控失败语义修复
- 新增更多业务模块的 analytics 接线点

## 预期结果

1. 当前已接线的首批 `auth` / `agents` 服务端事件在代码、字典和指标说明中使用同一套名称与字段口径。
2. 事件字典重新成为首批 analytics 服务端事件的可信真相源。
3. 后续 analytics step 可以在不重复解释历史命名分歧的前提下继续扩展。

## 影响范围

- `docs/tracking/event-dictionary.md`
- `docs/tracking/metrics-definition.md`
- `openspec/specs/analytics/spec.md`
- `apps/api/src/modules/auth/*`
- `apps/api/src/modules/agents/*`
- `apps/api/src/modules/analytics/*`
