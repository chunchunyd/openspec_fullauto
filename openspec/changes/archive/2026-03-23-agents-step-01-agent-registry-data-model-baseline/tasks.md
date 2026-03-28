# 任务拆解：Agents Step 01 Agent Registry 数据模型基线

## 1. 实施前门禁

- [x] 如果 `dev/agents` 不存在，则从最新 `dev` 切出 `dev/agents`
- [x] 从 `dev/agents` 切出 `feat/agents-step-01-agent-registry-data-model-baseline`
- [x] 阅读现有 `openspec/specs/agents/spec.md` 与 `openspec/specs/repository-structure/spec.md`
- [x] 确认当前 step 只建立 Agent registry 数据模型与模块基线，不混入 CRUD、public、知识或记忆接口

## 2. 数据模型与持久化锚点

- [x] 为 Agent registry 补齐最小 Prisma model、enum 与 owner relation
- [x] 明确最小基础资料字段、type、visibility 与 public status 的持久化锚点
- [x] 确认这些字段落在 `prisma/` 真相源，而不是在 `apps/api` 内并行维护另一份 schema

## 3. API 模块基线

- [x] 在 `apps/api/src/modules/agents` 建立最小 repository / service / module 落位
- [x] 明确 `agents` 模块只承接注册管理、主数据与状态归档，不承接 runtime 编排
- [x] 为后续 step 预留 owner 校验和读取边界，而不是提前把权限逻辑散落到 controller 外层

## 4. 文档与注释

- [x] 更新 `apps/api/README.md` 或等价模块说明，记录 `agents` 当前职责和非目标
- [x] 对非直观字段或状态枚举补必要注释，说明 owner / visibility / public status 的边界

## 5. 验证与测试

- [x] 为 Agent registry repository、数据映射或等价持久化边界补单元测试
- [x] 运行 Prisma generate / schema 校验与 `apps/api` 相关测试，确认新模型可被 API 模块稳定消费
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/agents-step-01-agent-registry-data-model-baseline` squash merge 回 `dev/agents`
- [x] 不在本 change 内执行 `dev/agents -> dev`，该操作由人工负责
