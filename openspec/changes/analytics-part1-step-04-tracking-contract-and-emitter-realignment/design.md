# 设计说明：Analytics Part1 Step 04 Tracking 契约与 Emitter 对齐收口

## 目标

- 让当前已接线的首批服务端 analytics 事件在“文档、指标、代码”三处恢复一一对应关系。
- 先解决“同一语义出现两套命名”的问题，再继续往后补 deployability 和 ingestion hardening。

## 边界

- 只处理当前已经落在 `auth`、`agents` 中的代表性事件，不顺手扩成全量服务端模块覆盖。
- 只处理稳定事件名称与关键 payload 字段，不在这一步引入新的聚合表或看板接口。
- 只收口 analytics tracking 契约，不改 audit-log 的 owner 边界。

## 方案

### 1. 先确定 canonical event contract

- 对当前已经发射的 `auth_login_*`、`auth_logout_*`、`agent_*` 事件做一次契约盘点。
- 对已有 tracking 字典已经存在的通用事件，优先沿用字典里的稳定命名，而不是继续保留实现期临时分叉出来的事件名。
- 如果某个当前已稳定的业务事件确实需要独立事件名，必须在同一个 change 中同步补入 `event-dictionary.md` 和 `metrics-definition.md`。

### 2. 让“结果态”进入 payload，而不是继续分裂顶层事件名

- 对登录成功、登录拦截这类共享同一业务语义的事件，优先复用统一顶层事件名，并通过 payload 中的结果字段承载 `succeeded` / `blocked` / `denied` 等差异。
- 这样可以让指标文档继续以统一事件名建立口径，同时保留失败态分析所需的细节。

### 3. 用 docs/tracking + analytics spec 共同约束代码

- `docs/tracking/event-dictionary.md` 记录事件名称、字段和版本。
- `docs/tracking/metrics-definition.md` 只引用已存在且已对齐的事件名。
- `openspec/specs/analytics/spec.md` 收紧 requirement，要求当前已接线 emitter 与 tracking 真相源保持一致，不允许“只改代码不改 tracking”。

## 风险与取舍

- 如果直接跟随当前代码命名更新文档，会把实现期临时命名固化为长期真相源；因此需要先判断哪些命名值得保留，哪些应该回归统一事件名。
- 如果只改文档不改代码，本次 review 暴露的问题不会消失；因此这一 change 需要把 emitter 调用点与 docs 一起收口。

## 验证重点

- 当前 `auth` / `agents` 中所有已接线 emitter 都能在字典里找到一一对应项。
- 指标文档不再引用代码中不存在的事件名。
- 相关单测或等价验证能覆盖至少一条 `auth` 和一条 `agents` 的契约对齐样例。
