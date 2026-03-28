# 任务拆解：Agents Step 08 分层记忆记录基线

## 1. 实施前门禁

- [x] 同步最新 `dev/agents`
- [x] 从 `dev/agents` 切出 `feat/agents-step-08-layered-memory-record-baseline`
- [x] 确认 `agents-step-03-agent-detail-and-profile-update` 已完成或达到可复用状态
- [x] 确认当前 step 只处理分层记忆记录锚点，不混入知识条目、runtime 自动写回或 chat 任务接线

## 2. 分层记忆数据模型

- [x] 为长期画像、长期设定、会话摘要和任务级临时记忆建立最小 layer 枚举与持久化锚点
- [x] 为记忆记录补最小生命周期字段，例如有效状态、过期或归档锚点
- [x] 保证记忆记录和知识条目保持独立模型与职责边界

## 3. 受控读取与最小写入边界

- [x] 建立 owner 或平台侧受控的记忆读取接口或等价 service 边界
- [x] 建立最小记忆写入 / 更新边界，避免后续能力绕过统一层直接散写
- [x] 明确各 layer 的基础校验和越权访问受控响应

## 4. 契约、文档与注释

- [x] 为新增读取或写入接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档，说明分层记忆与知识条目的区别
- [x] 对记忆 layer 语义与生命周期字段补必要注释

## 5. 验证与测试

- [x] 为不同 layer 的读写、越权访问和生命周期状态映射补单元测试、集成测试或等价验证
- [x] 验证记忆记录不会被误当作知识条目或公开 profile 字段返回
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/agents-step-08-layered-memory-record-baseline` merge 回 `dev/agents`
- [x] 不在本 change 内执行 `dev/agents -> dev`，该操作由人工负责
