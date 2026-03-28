# 任务拆解：运行时环境加载与数据库配置校验修正

## 1. 契约与范围确认

- [x] 为 `runtime-config` capability 建立本次 change 的 spec delta
- [x] 在 proposal/design 中明确本次问题属于运行时配置加载与数据库配置校验问题，而不是 health 契约再次变更
- [x] 明确本次 change 只修正本地运行时环境加载与数据库 fail-fast 行为，不扩展成完整配置中心建设

## 2. 运行时环境加载修正

- [x] 为 `apps/api` 建立稳定的本地环境加载方式，确保从 monorepo 根 `.env` 发现并注入运行时配置
- [x] 为 `apps/worker` 建立与 API 一致的本地环境加载方式
- [x] 明确环境变量优先级，保证已显式注入的部署环境变量不会被本地 `.env` 错误覆盖

## 3. 数据库配置校验修正

- [x] 在 `libs/database` 中提取数据库连接字符串解析/规范化 helper
- [x] 对 `DATABASE_URL` 增加最小校验：非空、去空白、去包裹引号、协议合法
- [x] 让 `PrismaService` 在启动阶段就对无效配置失败快速，并输出清晰错误信息

## 4. 验证与文档

- [x] 为连接字符串规范化与异常配置增加单元测试或等价验证
- [x] 验证缺失或错误 `DATABASE_URL` 时，应用在启动阶段即失败，而不是等到 `/health/ready`
- [x] 更新根 README，明确本地开发时 `.env` 的加载方式与排障说明
- [x] 在数据库配置 helper 或 PrismaService 附近补必要注释，解释为何需要 fail-fast 行为

### 手动验收步骤

1. **正常配置启动**
   ```bash
   pnpm dev-up
   pnpm dev-api
   ```
   - API 应正常启动
   - `GET http://localhost:3000/health/ready` 应返回真实 readiness 结果

2. **缺失数据库连接配置**
   - 临时移除或清空 `DATABASE_URL`
   - 重新启动 API 或 worker
   - 应在启动阶段直接失败，并输出明确的数据库配置错误

3. **带包裹引号的连接字符串**
   - 使用常见 `.env` 形式的 `DATABASE_URL=\"postgresql://...\"`
   - 重新启动服务
   - 应能被规范化后正常连接，而不是落入底层 SCRAM 类型错误
