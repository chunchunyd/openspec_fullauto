# Delta for Service Health

## ADDED Requirements

### Requirement: 系统必须暴露稳定且一致的健康检查端点

系统必须为 `api` 与 `worker` 暴露稳定且一致的健康检查端点，以支撑本地开发、联调和部署探针。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期规范端点至少包括：

- `GET /health`
- `GET /health/live`
- `GET /health/ready`


#### Scenario: API 暴露规范健康检查端点

- WHEN 开发者或运行时探针访问 API 的健康检查端点
- THEN API 必须在规范路径上返回对应结果
- AND 实际路径必须与仓库入口文档保持一致

#### Scenario: Worker 暴露规范健康检查端点

- WHEN 开发者或运行时探针访问 worker 的健康检查端点
- THEN worker 必须在规范路径上返回对应结果
- AND 不得同时保留语义冲突的重复健康检查入口

### Requirement: 系统必须让 readiness 反映应用关键依赖状态

系统必须让 readiness 反映应用当前关键依赖的最小可用状态，而不应仅以“进程仍在运行”代替就绪判断。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: API 关键依赖异常

- WHEN API 的数据库、Redis、queue 或其他关键依赖不可用
- THEN API 的 readiness 结果不得继续报告为 ready
- AND 调用方必须能够识别该运行时暂不适合接收正常流量

#### Scenario: Worker 关键依赖异常

- WHEN worker 的 queue、Redis、数据库或其他关键依赖不可用
- THEN worker 的 readiness 结果不得继续报告为 ready
- AND 调用方必须能够识别该运行时暂不适合处理后台任务
