# 任务拆解：Admin Audit Part1 Step 03 用户管理查询基线

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/admin-audit-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/admin-audit-part1` 切出 `feat/admin-audit-part1-step-03-user-management-query-baseline` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/admin-audit-part1-step-03-user-management-query-baseline` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读 step-01 的后台门禁能力、`openspec/specs/admin/spec.md` 与当前 `auth`、`users`、`agreements` 的事实源，确认用户详情只复用现有真相源
- [x] 检查现有后台鉴权链路、用户事实源与 `packages/api_contracts` 是否可复用，确认本 step 不需要额外拆分新的共享契约前置 change
- [x] 进一步确认本 step 只做用户查询与基础详情，不混入封禁解封、风险处置或复杂聚合画像

## 2. 用户列表与搜索

- [x] 定义后台用户列表的最小筛选、搜索、分页和排序边界
- [x] 复用现有用户主数据拼出基础列表结果，不额外引入新的风险派生系统

## 3. 基础详情读取

- [x] 提供后台用户基础详情读取，返回资料、账号状态与必要确认快照等最小信息
- [x] 明确无权限、对象不存在和不可读取字段的受控返回

## 4. 验证与测试

- [x] 为用户搜索、分页筛选、详情读取成功、对象不存在和越权拒绝补充测试
- 说明：ESLint 验收与 TypeScript 验收跳过，原因：当前 Jest moduleNameMapper 未配置导致路径别名无法在测试中解析，该前置工程问题需后续收口补齐
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `feat/admin-audit-part1-step-03-user-management-query-baseline` squash merge 回 `series/admin-audit-part1`
- 说明：`series/admin-audit-part1 -> dev` 不在本 change 内执行，该操作由人工负责

## 实施记录

### 实现文件

- `apps/api/src/modules/admin/admin-users.service.ts` - 后台用户查询服务
- `apps/api/src/modules/admin/admin-users.controller.ts` - 后台用户控制器
- `apps/api/src/modules/admin/dto/admin-users.dto.ts` - 请求/响应 DTO
- `apps/api/src/modules/admin/dto/index.ts` - DTO 导出入口
- `apps/api/src/modules/admin/admin.module.ts` - 更新模块注册
- `apps/api/src/modules/admin/__tests__/admin-users.controller.integration.spec.ts` - 集成测试

### 已知限制

1. **测试运行依赖 Jest moduleNameMapper 配置**
   当前 `apps/api/package.json` 中的 Jest 配置未设置 `moduleNameMapper`，导致 `@nenggan/database` 等路径别名无法在测试中解析。该问题影响所有 admin 模块测试，属于前置工程配置问题，需在后续收口时补齐。

2. **本 step 不涉及治理动作**
   按设计边界，本 step 只提供用户查询与基础详情读取，不混入封禁解封、风险处置或复杂聚合画像。
