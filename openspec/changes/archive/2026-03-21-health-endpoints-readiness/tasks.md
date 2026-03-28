# 任务拆解：服务健康检查路径与 Readiness 修正

## 1. 契约与规格

- [x] 为 `service-health` capability 建立本次 change 的 spec delta
- [x] 在 proposal/design 中确认规范 health 端点与 readiness 语义
- [x] 明确本次 change 只修正 health 行为，不顺带展开完整 observability 重构

## 2. API 健康检查修正

- [x] 修正 API health controller 的路由声明，确保真实路径为 `/health`、`/health/live`、`/health/ready`
- [x] 为 API 建立应用级 readiness 检查，至少覆盖数据库、Redis 与 queue 的最小依赖状态
- [x] 对 API health / readiness 的职责边界补必要注释或模块说明

## 3. Worker 健康检查修正

- [x] 修正 worker health controller 的路由声明，确保真实路径为 `/health`、`/health/live`、`/health/ready`
- [x] 清理 worker 中重复或冲突的静态 `/health` 暴露方式
- [x] 为 worker 建立应用级 readiness 检查，至少覆盖 queue / Redis 与当前关键依赖状态

## 4. 验证与文档

- [x] 为 API 和 worker 的 health 路由与 readiness 行为补单元测试或等价验证
- [x] 验证依赖异常时 readiness 不再误报 ready
- [x] 更新根 README 中健康检查端点说明
- [x] 如果暂不补完整自动化测试，明确原因并保留可重复执行的手动验收步骤

### 手动验收步骤

1. **启动服务**：
   ```bash
   pnpm dev-up          # 启动 PostgreSQL 和 Redis
   pnpm dev-api         # 启动 API (端口 3000)
   pnpm dev-worker      # 启动 Worker (端口 3001)
   ```

2. **验证健康检查路由**：
   ```bash
   # API
   curl http://localhost:3000/health         # 应返回完整健康状态
   curl http://localhost:3000/health/live    # 应返回 { status: 'ok', message: 'alive' }
   curl http://localhost:3000/health/ready   # 应检查数据库和 Redis 状态

   # Worker
   curl http://localhost:3001/health         # 应返回完整健康状态
   curl http://localhost:3001/health/live    # 应返回 { status: 'ok', message: 'alive' }
   curl http://localhost:3001/health/ready   # 应检查数据库和 Redis 状态
   ```

3. **验证依赖异常检测**：
   - 停止 PostgreSQL：readiness 应返回 `unhealthy`
   - 停止 Redis：readiness 应返回 `unhealthy`

4. **验证无重复路由**：
   - Worker 的 `GET /health` 应由 HealthController 处理
   - Worker 的 `AppController` 不再暴露重复的 `/health` 端点
