# Delta for API Contracts

## ADDED Requirements

### Requirement: 共享 OpenAPI 产物必须覆盖已交付的公开 HTTP 路径

系统必须让导出的共享 OpenAPI 产物覆盖当前已交付的公开 HTTP 路径与代表性契约结果，以便消费方能基于同一份派生产物联调。 The system MUST ensure the exported shared OpenAPI artifact covers delivered public HTTP paths and their representative contract shapes.

#### Scenario: 新增公开 HTTP 路径后执行 openapi-export

- WHEN API 服务新增或实质修改一条公开 HTTP 路径
- THEN 重新导出的共享 OpenAPI 产物必须包含该路径
- AND 结果中必须体现代表性的成功或错误契约结构

#### Scenario: 消费方读取共享契约

- WHEN `mobile`、`admin-web` 或其他消费方读取共享 OpenAPI 产物
- THEN 它们必须能够从该产物中看到当前已交付的公开路径
- AND 不应继续依赖缺失路径的旧契约推进正式接入
