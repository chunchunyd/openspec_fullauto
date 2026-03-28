# Delta for Mobile Foundation

## ADDED Requirements

### Requirement: mobile foundation 层必须提供最小结构化埋点钩子

mobile foundation 层必须提供最小结构化埋点钩子，以支持启动、路由分流、request 结果和本地会话恢复的统一事件接线。 The mobile foundation MUST provide minimal structured telemetry hooks for startup, routing, request results, and local session restoration.

#### Scenario: foundation 路径触发 hook

- WHEN 应用启动、路由分流、request 成功失败或 session 恢复发生
- THEN foundation 层必须能够通过统一接口发出最小结构化事件
- AND 不得要求各 feature 各自重新发明基础层 telemetry 入口

#### Scenario: 本地开发环境不接第三方供应商

- WHEN 当前环境未接入真实 analytics 供应商
- THEN foundation 层必须仍可通过 no-op、debug 或等价实现完成受控接线
- AND 基础层不得直接把真实供应商 SDK 视为强依赖

#### Scenario: foundation 事件包含敏感字段

- WHEN foundation hook 试图记录手机号、token 或 session snapshot 等敏感信息
- THEN 这些字段必须被省略、脱敏或映射为受控标识
- AND 不得直接输出完整敏感值
