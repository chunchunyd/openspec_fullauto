# 设计说明：Public Content Step 16 互动信号回归护栏加固

## 目标

本 step 的目标不是重新设计 signal 结构，而是把当前已经承诺存在的 signal 发射点真正纳入可回归验证的测试护栏中。

## 当前缺口

当前生产代码已经在以下主线发信号：

- comments 成功创建后发 `POST_COMMENTED`
- follows 成功关注 / 取消关注后发 `AGENT_FOLLOWED` / `AGENT_UNFOLLOWED`
- reports 成功提交后发举报相关 signal

但对应 tests 目前大多只注入了 mock service，本身并不验证这些调用是否真的发生，也不验证动作类型与目标类型是否匹配。

## 方案选择

### 1. 只覆盖代表性成功路径

本 step 先补最小但高信号的成功路径断言，而不是试图为所有失败分支和所有 metadata 细节一次性穷举。

推荐至少覆盖：

- comments: `POST_COMMENTED`
- follows: `AGENT_FOLLOWED`
- reports: 至少一条举报 signal 的 action / targetType / targetId 对齐

### 2. 断言当前 helper API，而不是绕过到更底层实现

comments 和 follows 当前分别通过 `emitPostSignal` / `emitAgentSignal` 发信号；reports 当前直接调用 `emit`。

测试应优先围绕这些实际调用点写断言，避免用过于抽象的 mock 让测试失去对当前 signal surface 的保护价值。

## 非目标

本 step 不处理：

- signal 持久化
- 新的 targetType 或 action 扩张
- `packages/event_schema` 的正式事件契约沉淀
