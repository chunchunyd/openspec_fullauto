# 任务拆解：P0 短信共享层基建

## 1. 契约与规格

- [x] 为 `sms` capability 建立本次 change 的 spec delta
- [x] 在 proposal/design 中确认：共享短信层职责、auth 边界、queue 边界、debug provider 范围
- [x] 明确本次 change 不承载验证码缓存、频控与完整 auth 流程

## 2. `libs/sms` 共享运行时基础层

- [x] 整理 `libs/sms` 的可复用包结构、公开入口与 README
- [x] 定义统一 `SmsPort`、发送请求模型与发送结果模型
- [x] 定义 provider 选择与配置读取方式
- [x] 补齐至少一个 fake / debug provider
- [x] 明确 provider 错误分类与最小日志字段

## 3. 与共享层和业务层的边界

- [x] 明确 `auth` 未来应如何通过共享短信层发送验证码，而不是在模块内部直接接供应商
- [x] 明确后续 queue / worker 如果要异步发短信，应如何复用 `libs/sms`
- [x] 明确 observability 接入点，保证发送日志与错误日志字段一致

## 4. 验证与测试

- [x] 为请求模型、provider 选择或 fake provider 的关键逻辑补单元测试
- [x] 规划本地开发环境下的最小验收路径
- [x] 如果暂不接真实供应商，明确原因并保留可重复执行的手动验收步骤

## 5. 文档与注释

- [x] 更新 `libs/sms/README.md`
- [x] 如环境变量、开发入口或调试方式发生变化，更新根 README 或相关入口文档
- [x] 对调试替身、脱敏边界和 provider 选择规则补必要注释或模块说明
