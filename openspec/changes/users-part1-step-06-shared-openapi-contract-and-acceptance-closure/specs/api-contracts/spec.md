# Delta for API Contracts

## MODIFIED Requirements

### Requirement: 共享 OpenAPI 产物必须覆盖已交付的公开 HTTP 路径

系统必须让导出的共享 OpenAPI 产物覆盖当前已交付的公开 HTTP 路径与代表性契约结果，包括成功结果、受控业务错误以及请求校验失败结果，以便消费方能基于同一份派生产物联调。 The system MUST ensure the exported shared OpenAPI artifact covers delivered public HTTP paths and representative success, business-error, and request-validation contract shapes.

#### Scenario: 新增公开 HTTP 路径后执行 openapi-export

- WHEN API 服务新增或实质修改一条公开 HTTP 路径
- THEN 重新导出的共享 OpenAPI 产物必须包含该路径
- AND 结果中必须体现代表性的成功、业务错误或请求校验错误契约结构

#### Scenario: users 自我资料与设置路径完成契约收口

- WHEN `/users/me`、`/users/me/settings` 或等价 users 自我资料路径已经作为当前已交付接口存在
- THEN 共享 OpenAPI 产物必须包含这些路径及其代表性的成功、未认证和校验失败结果
- AND 消费方不得继续依赖缺失这些路径的旧契约推进正式接入

#### Scenario: 消费方读取共享契约

- WHEN `mobile`、`admin-web` 或其他消费方读取共享 OpenAPI 产物
- THEN 它们必须能够从该产物中看到当前已交付的公开路径
- AND 不应继续依赖缺失路径或缺失代表性响应结构的旧契约推进正式接入
