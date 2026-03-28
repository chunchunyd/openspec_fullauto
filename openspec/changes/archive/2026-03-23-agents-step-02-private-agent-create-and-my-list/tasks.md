# 任务拆解：Agents Step 02 私有 Agent 创建与我的列表

## 1. 实施前门禁

- [x] 同步最新 `dev/agents`
- [x] 从 `dev/agents` 切出 `feat/agents-step-02-private-agent-create-and-my-list`
- [x] 确认 `agents-step-01-agent-registry-data-model-baseline` 已完成或达到可复用状态
- [x] 确认当前 step 只处理私有 Agent 创建与我的列表，不混入详情、更新和 public read

## 2. owner-scoped 创建与列表

- [x] 建立已登录用户创建私有 Agent 的最小接口与 DTO
- [x] 约束新建 Agent 默认落为受控的私有 visibility / public status
- [x] 建立"我的 Agent 列表"接口，并返回最小可展示资料

## 3. 鉴权与边界

- [x] 复用现有 auth guard / current user 注入边界，避免在 `agents` 模块内再造一套鉴权机制
- [x] 明确创建与列表只允许返回当前用户拥有的 Agent
- [x] 不允许通过参数伪造 ownerId 或越权读取他人的私有 Agent 列表

## 4. 契约、文档与注释

- [x] 为新增接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档，说明"我的 Agent"入口和非目标
- [x] 对默认 visibility / public status 约束补必要注释

## 5. 验证与测试

- [x] 为创建成功、创建参数校验失败和"我的列表"查询补集成测试或等价验证
- [x] 验证未登录或越权场景不会返回他人的私有 Agent 数据
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/agents-step-02-private-agent-create-and-my-list` squash merge 回 `dev-agents`
- [x] 不在本 change 内执行 `dev-agents -> dev`，该操作由人工负责

