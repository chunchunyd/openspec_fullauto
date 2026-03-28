# 变更提案：Mobile Foundation Step 05 基础埋点钩子

## 为什么要做

需求基线已经要求客户端为埋点与统一异常处理预留能力，但 mobile 当前还没有任何稳定的 foundation telemetry 落点。

如果这一层一直缺失：

- 启动、路由分流、request 成功失败和本地会话恢复都没有统一钩子
- 后续 auth feature 容易直接耦合具体 analytics SDK
- 基础层很难在不引入真实供应商依赖的前提下做本地调试和验证

因此需要把最小 telemetry hooks 单独拆出来，作为 mobile foundation 的最后一层前置基建。

## 本次变更包含什么

本次变更聚焦移动端基础埋点钩子，范围包括：

- 定义 foundation 层最小 telemetry 接口与事件钩子落点
- 为启动、路由分流、request 结果和 session 恢复预留统一 hook
- 提供不依赖真实第三方供应商的本地或 no-op 实现
- 明确敏感字段脱敏边界

## 本次变更不包含什么

本次变更不包含以下内容：

- 完整 analytics 事件字典
- 具体第三方埋点供应商 SDK 接线
- 运营分析报表
- 业务 feature 级埋点细节

## 预期结果

完成后，项目应具备以下结果：

1. foundation 层有统一 telemetry hook，而不是各 feature 自己随意打印或上报
2. 启动、路由、request 与 session 恢复都能在不绑定真实 SDK 的前提下发出最小事件
3. 后续 auth 和其他 feature 可以在此基础上扩展埋点，而不是重建接口

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/core`
- `apps/mobile/lib/app`
- `apps/mobile/README.md`
