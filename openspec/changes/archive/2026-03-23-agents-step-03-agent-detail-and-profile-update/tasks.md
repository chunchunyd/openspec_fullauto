# 任务拆解：Agents Step 03 Agent 详情与资料更新

## 1. 实施前门禁

- [x] 同步最新 `dev/agents`
- [x] 从 `dev/agents` 切出 `feat/agents-step-03-agent-detail-and-profile-update`
- [x] 确认 `agents-step-02-private-agent-create-and-my-list` 已完成或达到可复用状态
- [x] 确认当前 step 只处理 owner-scoped 详情与基础资料更新，不混入 public read、策略或知识/记忆子能力

## 2. 详情与更新接口

- [x] 建立单个 Agent 详情读取接口，返回当前管理所需的最小完整资料
- [x] 建立基础资料更新接口，并约束允许修改的字段范围
- [x] 明确不存在 Agent、越权访问和非法更新输入的受控响应边界

## 3. owner 校验与边界

- [x] 保证详情与更新只对 Agent owner 放行
- [x] 不允许通过 public status 未生效的 Agent 绕过 owner 校验进入管理详情
- [x] 为后续策略、知识和记忆子资源预留统一的 Agent 读取入口

## 4. 契约、文档与注释

- [x] 为详情与更新接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档，说明 owner-scoped 详情与更新边界
- [x] 对可更新字段与不可更新字段补必要注释

## 5. 验证与测试

- [x] 为详情读取成功、越权访问、更新成功和更新参数校验失败补集成测试或等价验证
- [x] 验证未登录或非 owner 无法读取或修改私有 Agent 管理详情
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/agents-step-03-agent-detail-and-profile-update` squash merge 回 `dev/agents`
- [x] 不在本 change 内执行 `dev/agents -> dev`，该操作由人工负责
