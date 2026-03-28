# 变更提案：Public Content Step 16 互动信号回归护栏加固

## 为什么要做

step-11 和 step-13 已经把 comments、follows、reports 等动作接入了 `BehaviorSignalService`，但最新验收表明对应 service 测试当前只恢复到了“provider 不缺失、测试能跑起来”的程度，还没有为代表性成功路径补齐行为信号断言。

这会留下一个很危险的空窗：后续如果有人重构时意外删掉 `emitPostSignal`、`emitAgentSignal` 或 `emit` 调用，现有 tests 仍可能全部通过，结构化行为信号却已经静默失效。

本 step 继续沿用 `public-content` 作为 series prefix，只收口 public-content 互动信号的回归护栏，不引入新的信号类型、事件持久化或分析平台扩张。

## 本次变更包含什么

- 为 comments、follows、reports 的代表性成功路径补齐行为信号断言
- 对齐测试中的 mock / helper，让 signal 调用契约可以被稳定验证
- 确认当前 public-content 已承诺的最小结构化信号不会在后续重构中静默丢失

## 本次变更不包含什么

- 新的行为信号类型
- `packages/event_schema` 的扩张或事件持久化
- 互动摘要聚合逻辑返工

## 预期结果

1. comments、follows、reports 的成功路径测试会明确校验对应 signal 是否被发出。
2. 如果后续有人删掉或改坏这些 signal 调用，tests 会第一时间失败。
3. public-content 互动信号主线具备最小但真实可依赖的回归护栏。

## 影响范围

- `apps/api/src/modules/interactions/__tests__/*`
- 必要时的 `apps/api/src/modules/interactions/*`
