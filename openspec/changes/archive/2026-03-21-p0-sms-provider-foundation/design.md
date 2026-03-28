# 设计说明：P0 短信共享层基建

## 目标

本次设计的目标不是先做完整短信业务，而是先建立一套最小但稳定的共享短信层，让后续 `auth` 能直接复用。

重点解决四件事：

1. `libs/sms` 到底负责什么
2. 业务模块如何通过共享抽象发送短信
3. 本地开发和测试如何不依赖真实短信供应商
4. 后续 queue 与 observability 应如何接入短信层

## 分层模型

### 1. 共享短信运行时层：`libs/sms`

职责：

- 定义短信发送 port
- 统一请求 / 结果模型
- provider adapter 接线
- provider 选择与配置读取
- fake / debug provider
- 最小日志与错误分类边界

不负责：

- 验证码缓存、频控和验证码校验
- 业务模块自己的模板语义和流程编排
- 队列投递本身

### 2. 业务模块层

职责：

- 组织自己的短信业务语义
- 例如“发送登录验证码”“发送风控提醒”
- 决定何时调用共享短信 port

这意味着：

- `auth` 负责“什么时候给谁发验证码”
- `libs/sms` 负责“怎么把短信发出去”

## 首期能力范围

首期建议只做后续最需要复用的部分：

- `SmsPort`
- 统一的 `SendSmsCommand`
- 统一的发送结果类型
- fake / debug provider
- 至少一种可替换的 provider adapter 结构

本次刻意不纳入：

- 异步投递与队列化发送
- 多供应商自动降级
- 模板中心
- 营销短信系统

## 为什么先做同步短信基线

虽然未来短信发送很可能会接 queue，但当前更稳的做法是先建立同步发送基线。

原因：

- `auth` 最先需要的是“有一个共享短信层可调用”
- 如果一上来把 queue、provider、模板、重试全部绑死，change 会过大
- 同步短信 port 建好后，后续完全可以在业务层或 queue change 中把“调用时机”改为异步

因此这次设计遵循：

- `libs/sms` 先解决发送抽象
- queue 后续只负责“是否异步触发发送”

## 请求与结果模型

建议首期定义统一请求模型，例如：

- `scene`
- `recipient`
- `templateId` 或等价模板标识
- `templateParams`
- `correlationId`

统一结果至少应包含：

- `provider`
- `status`
- `providerMessageId`（如可得）
- `errorCode`（失败时）

这样后续：

- `auth`
- 通知
- 审核

都能在不直接依赖供应商 SDK 响应格式的前提下复用短信发送能力。

## fake / debug provider

本地开发和测试必须有一套稳定替身。

建议首期提供：

- fake provider
  - 永远不真正发送短信
  - 返回可预测结果
- debug provider
  - 允许把验证码或模板参数以受控方式输出到日志或调试介质
  - 但必须遵守脱敏与环境限制

要求：

- 生产环境不得默认启用 debug provider
- 不得把验证码明文随意打印为普通信息日志
- 调试输出方式应在 README 中明确说明

## 错误与日志边界

首期建议至少区分：

- 配置错误
- provider 调用失败
- provider 响应异常
- 可重试失败与不可重试失败

与 `p0-observability-runtime-foundation` 的关系：

- `libs/sms` 应复用共享 logger 能力
- 日志应保留 `scene`、`provider`、`correlationId` 等基础字段
- 手机号、验证码、token 等敏感字段必须脱敏

## 与 auth 的边界

这次必须把上次容易混掉的边界钉死：

- `auth`
  - 验证码生成
  - 冷却时间与频控
  - 验证码校验
  - 何时调用短信发送
- `libs/sms`
  - provider 接线
  - 发送抽象
  - 调试替身
  - 结果模型

`auth` 不应再内部创建独立 provider factory。

## 与 queue 的关系

未来如果短信发送要异步化，推荐关系如下：

- 业务模块决定发送场景
- queue 决定是否异步投递
- `worker` 消费 job
- 具体发送仍调用 `libs/sms`

也就是说：

- `queue` 不替代 `libs/sms`
- `libs/sms` 也不负责 job 管理

## 首期目录建议

```txt
libs/sms/
├─ README.md
└─ src/
   ├─ index.ts
   ├─ sms.module.ts
   ├─ sms.port.ts
   ├─ sms.types.ts
   ├─ sms.tokens.ts
   └─ providers/
      ├─ fake-sms.provider.ts
      └─ ...
```

如果当前暂时不准备完整拆开文件，也至少应保证：

- port
- types
- provider

这三类职责不要继续停留在空文件里。

## 与后续 change 的关系

该 change 完成后，后续最直接受益的是：

- `auth` 验证码发送
- 未来通知类短信
- 未来可能由 `worker` 异步执行的短信任务

后续 change 不再重新争论“短信 provider 放哪、调试替身怎么做、错误结果怎么表达”。
