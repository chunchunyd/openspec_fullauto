# 任务拆解：Agents Step 06 公开申请提交与状态读取

## 1. 实施前门禁

- [x] 同步最新 `dev/agents`
- [x] 从 `dev/agents` 切出 `feat/agents-step-06-public-application-submission-and-status`
- [x] 确认 `agents-step-04-visibility-and-public-read-boundary` 与 `agents-step-05-policy-metadata-and-maturity-read-model` 已完成或达到可复用状态
- [x] 确认当前 step 只处理申请提交与状态读取，不混入 admin 审批决定实现

## 2. 公开申请数据与前置校验

- [x] 建立公开申请提交所需的最小状态锚点或等价申请记录
- [x] 明确申请提交前的 owner、public status 和成熟度前置校验
- [x] 不允许未满足前置条件的 private Agent 直接绕过申请边界进入公开状态

## 3. 申请接口与状态读取

- [x] 建立 owner-scoped 的公开申请提交接口
- [x] 建立 owner-scoped 的公开申请状态读取结果
- [x] 明确重复提交、已在申请中和当前状态不允许提交的受控响应

## 4. 契约、文档与注释

- [x] 为公开申请接口补 Swagger / OpenAPI 描述，并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档，说明当前只覆盖申请提交与状态读取，不包含审批决定
- [x] 对申请状态流转和非目标补必要注释

## 5. 验证与测试

- [x] 为申请成功、重复提交、前置条件不满足和状态读取补集成测试或等价验证
- [x] 验证普通用户无法替他人提交公开申请
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/agents-step-06-public-application-submission-and-status` squash merge 回 `dev/agents`
- [x] 不在本 change 内执行 `dev/agents -> dev`，该操作由人工负责

