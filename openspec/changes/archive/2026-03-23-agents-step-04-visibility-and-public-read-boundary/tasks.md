# 任务拆解：Agents Step 04 可见性与 Public Read 边界

## 1. 实施前门禁

- [x] 同步最新 `dev/agents`
- [x] 从 `dev/agents` 切出 `feat/agents-step-04-visibility-and-public-read-boundary`
- [x] 确认 `agents-step-03-agent-detail-and-profile-update` 已完成或达到可复用状态
- [x] 确认当前 step 只处理读取边界，不混入公开申请提交、策略配置或知识/记忆子能力

## 2. public read 与访问判定

- [x] 建立受控的 public read 读取边界，并只返回公开消费所需字段
- [x] 明确 private、申请中、被拒绝、下线等状态下的读取策略
- [x] 抽出可复用的访问判定逻辑，避免 `chat`、`content` 等后续模块各自重写

## 3. owner 管理边界隔离

- [x] 保持 owner 管理详情与 public read 的接口语义分离
- [x] 确认 public read 不会返回仅供 owner 管理使用的敏感或内部字段
- [x] 确认 private Agent 不会因为错误的状态映射被普通用户读取

## 4. 契约、文档与注释

- [x] 为 public read 接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档，说明 public read 与管理读取边界
- [x] 对可见性 / public status 的判定分支补必要注释

## 5. 验证与测试

- [x] 为公开可读、私有拒绝、状态不允许读取等场景补集成测试或等价验证
- [x] 验证非 owner 无法通过 public read 获取 private Agent 的管理字段
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/agents-step-04-visibility-and-public-read-boundary` squash merge 回 `dev/agents`
- [x] 不在本 change 内执行 `dev/agents -> dev`，该操作由人工负责

