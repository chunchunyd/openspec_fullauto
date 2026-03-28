# 任务拆解：P0 对象存储共享层基建

## 1. 契约与规格

- [x] 为 `storage` capability 建立本次 change 的 spec delta
- [x] 在 proposal/design 中确认：共享存储层职责、content 边界、queue 边界、fake / local provider 范围
- [x] 明确本次 change 不承载完整媒体处理流水线和上传业务流程

## 2. `libs/storage` 共享运行时基础层

- [x] 整理 `libs/storage` 的可复用包结构、公开入口与 README
- [x] 定义统一 `StoragePort`、上传请求模型与上传结果模型
- [x] 定义 provider 选择与配置读取方式
- [x] 补齐至少一个 fake 或 local provider
- [x] 明确对象标识、访问 URL 与最小元信息边界

## 3. 与共享层和业务层的边界

- [x] 明确 `content` 未来应如何通过共享存储层处理帖子图片与封面，而不是直接接供应商 SDK
- [x] 明确后续 queue / worker 如果要做媒体处理任务，应如何复用 `libs/storage`
- [x] 明确 observability 接入点，保证上传日志与错误日志字段一致

## 4. 验证与测试

- [x] 为请求模型、provider 选择或 fake / local provider 的关键逻辑补单元测试
- [x] 规划本地开发环境下的最小验收路径
- [x] 如果暂不接真实对象存储，明确原因并保留可重复执行的手动验收步骤

## 5. 文档与注释

- [x] 更新 `libs/storage/README.md`
- [x] 如环境变量、开发入口或调试方式发生变化，更新根 README 或相关入口文档
- [x] 对对象标识、访问 URL 边界和 provider 选择规则补必要注释或模块说明
