# 设计说明：Auth Step 07 登录风险信号加固

## 目标

这个 step 不是做完整风控系统，而是给 auth 增加最小可用的风险信号与受控限制。

建议覆盖：

- 请求来源摘要
- 设备标识或设备摘要
- 与发送频控、校验失败次数的联动
- 必要日志和错误上下文

## 依赖

- 复用 `auth-step-02` 的发送冷却与频控
- 复用 `auth-step-03` 的失败次数控制
- 复用 `auth-step-04` / `auth-step-06` 的会话与设备上下文

## 建议流程

```text
incoming auth request
    ->
extract request source / device hints
    ->
combine with existing rate / failure state
    ->
classify: allow / limited / reject
    ->
log structured auth risk context
```

## 设计原则

- 先做最小信号，不追求一次性完整设备指纹
- 先做受控限制和留痕，不把所有异常都升级成强拦截
- 风险结果应能解释给后续排查和治理使用

## 失败场景

- 如果风险信号只写日志、不进入 auth 判定，实际防护价值会很弱
- 如果风险判断没有结构化日志，后续很难解释用户为什么被限制
- 如果把所有异常都强拦截，会增加误伤和联调成本
