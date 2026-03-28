# 任务拆解：Agents Step 05 策略 Metadata 与成熟度读模型

## 1. 实施前门禁

- [x] 同步最新 `dev/agents`
- [x] 从 `dev/agents` 切出 `feat/agents-step-05-policy-metadata-and-maturity-read-model`
- [x] 确认 `agents-step-03-agent-detail-and-profile-update` 已完成或达到可复用状态
- [x] 确认当前 step 只处理策略 metadata 与成熟度读模型，不混入公开申请、知识或记忆子能力

## 2. 数据模型与管理边界

- [x] 为平台侧策略 metadata 建立最小持久化锚点，例如 persona、行为边界、禁用主题和风格偏好
- [x] 为成熟度建立最小字段/等价读模型锚点，避免在后续公开流程里临时拼装
- [x] 明确这些字段属于平台管理元数据，而不是 runtime prompt 编排真相源

## 3. 读取与更新接口

- [x] 在 owner 管理详情中补充策略 metadata 与成熟度读取结果
- [x] 建立 owner-scoped 的策略 metadata 更新接口
- [x] 明确成熟度在本 step 作为读模型返回，不混入复杂计算引擎

## 4. 契约、文档与注释

- [x] 为新增或更新接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档，说明策略 metadata 与成熟度边界
- [x] 对”平台管理元数据”与”runtime 编排信息”的区别补必要注释

## 5. 验证与测试

- [x] 为策略 metadata 更新、成熟度读取和越权访问补集成测试或等价验证
- [x] 验证后续详情读取能稳定返回最新策略 metadata 与成熟度结果
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/agents-step-05-policy-metadata-and-maturity-read-model` squash merge 回 `dev/agents`
- [x] 不在本 change 内执行 `dev/agents -> dev`，该操作由人工负责

