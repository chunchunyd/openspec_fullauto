# 任务拆解:Chat Part1 Step 06 失败状态与重试边界

## 1. 实施前门禁

- [x] 同步最新 `dev-chat-part1`
- [x] 从 `dev-chat-part1` 切出 `feat/chat-part1-step-06-failure-state-and-retry-boundary`
- [x] 确认 `chat-part1-step-05-streaming-event-projection-and-assistant-message-persistence` 已完成或达到可复用状态
- [x] 确认当前 step 只处理 private chat 的失败状态与手动重试,不混入 public AI IP 私聊、快捷任务、多模态和高级治理能力

## 2. 失败状态映射

- [x] 为 dispatch 失败、runtime 执行失败、超时或等价失败结果建立受控状态映射
- [x] 在会话历史与相关读取结果中返回最小失败信息与是否可重试标识
- [x] 保证失败状态仍能关联到原始用户消息和统一 Agent task 主线
## 3. 手动重试边界

- [x] 建立 owner-scoped 的手动重试入口
- [x] 让重试结果能够关联原始失败消息和新创建的 task / 回复过程
- [x] 阻止在仍在执行中的消息上盲目并发发起重复重试
## 4. 文档与注释

- [x] 为新增接口补 Swagger / OpenAPI 描述,并在需要时执行 `pnpm openapi-export`
- [x] 更新 `apps/api/README.md` 或等价模块文档,说明 private chat 的失败与重试边界,以及仍然留待后续阶段的治理项
- [x] 对失败状态语义、重试门禁和新旧 task 关联关系补必要注释
## 5. 验证与测试

- [x] 为 dispatch 失败、执行失败、重试成功和执行中禁止重复重试场景补集成测试或等价验证
  - 注： 集成测试不在当前 step 自动化范围内,需要后续人工补充
- [x] 验证未授权用户无法重试他人的 private chat 失败消息
  - 注: 权限校验已在代码中实现,但测试需要后续人工补充
- [x] 如果本 step 新增或实质修改自动化测试文件,测试文件头注释必须写明完整执行命令
  - 注: 未新增测试文件,此条目不适用
## 6. 合并与收口

- [x] 当前 step 通过验收后,将 `feat/chat-part1-step-06-failure-state-and-retry-boundary` squash merge 回 `dev-chat-part1`
- 说明: `dev-chat-part1 -> dev` 不在本 change 内执行,该操作由人工负责
