# 任务拆解：Agents Step 07 文本知识条目管理

## 1. 实施前门禁

- [x] 同步最新 `dev/agents`
- [x] 从 `dev/agents` 切出 `feat/agents-step-07-text-knowledge-entry-management`
- [x] 确认 `agents-step-03-agent-detail-and-profile-update` 已完成或达到可复用状态
- [x] 确认当前 step 只处理文本知识条目，不混入分层记忆、向量索引或 runtime 检索编排

## 2. 知识数据模型与 owner 边界

- [x] 为文本知识条目建立最小持久化模型与处理状态锚点
- [x] 明确知识条目与 Agent owner 的归属关系
- [x] 不允许知识条目长期寄存在 profile 文本或其他无生命周期字段中

## 3. 知识管理接口

- [x] 建立 owner-scoped 的知识新增、列表、详情、更新和删除接口
- [x] 返回最小处理状态、更新时间和受控元数据
- [x] 明确已删除、越权访问和非法输入的受控响应

## 4. 契约、文档与注释

- [x] 为知识管理接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档，说明当前知识条目边界和非目标
- [x] 对知识条目状态和后续索引/检索非目标补必要注释

## 5. 验证与测试

- [x] 为知识新增、读取、更新、删除和越权访问补集成测试或等价验证
- [x] 验证 owner 之外的用户无法管理私有 Agent 的知识条目
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/agents-step-07-text-knowledge-entry-management` squash merge 回 `dev/agents`
- [x] 不在本 change 内执行 `dev/agents -> dev`，该操作由人工负责

