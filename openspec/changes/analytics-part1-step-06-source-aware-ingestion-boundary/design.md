# 设计说明：Analytics Part1 Step 06 Source-aware Ingestion Boundary

## 目标

- 让 raw event ingestion 真正保留事件来源语义，而不是继续把所有事件默认折叠为 `SERVER`。

## 边界

- 只处理 analytics 模块内部的 ingestion / repository / safe emitter 语义。
- 不在这一步暴露新的 HTTP collector，也不接入移动端 SDK。
- 不在这一步处理 duplicate 并发冲突的最终语义。

## 方案

### 1. `ingestRawEvent` 显式接受来源

- `IngestRawEventInput` 需要显式表达来源语义。
- raw ingestion 入口不再偷偷硬编码 `SERVER`，避免未来客户端路径复用时被静默写错。

### 2. 服务端 facade 继续屏蔽底层细节

- `emitServerEvent` / `emitServerEventSafe` 保留“业务模块只传事件名 + payload + 最小上下文”的 façade 语义。
- `SERVER` 来源由 analytics facade 内部补齐，而不是让业务模块四处散落来源枚举。

### 3. 用测试锁住两类路径

- 至少覆盖：
  - raw ingestion 写入 `CLIENT`
  - raw ingestion 写入 `SERVER`
  - server emitter 自动写入 `SERVER`

## 风险与取舍

- 如果给 raw ingestion 保留默认 `SERVER`，未来客户端路径最容易再次静默回退到错误来源。
- 如果让业务模块直接传来源，会把 analytics 底层细节重新扩散到各业务模块，因此 façade 仍应保留默认封装。

## 验证重点

- `CLIENT` / `SERVER` 两类来源都能稳定落库。
- 服务端 façade 的调用方式不变，来源语义由 analytics 模块内部负责。
