# 任务拆解：Auth Step 01 认证数据模型基线

## 1. 实施前门禁

- [x] 从最新 `dev` 切出 `feat/auth-step-01-data-model-baseline` 并确认主项目工作树边界
- [x] 再次阅读 `openspec/specs/auth/spec.md`、`openspec/specs/repository-structure/spec.md` 和本 change 设计说明
- [x] 确认本 step 只建设 auth 数据模型基线，不夹带短信、验证码或 token 签发实现

## 2. 契约与数据模型

- [x] 为 `auth` capability 建立本次 step 的 spec delta
- [x] 设计并确认用户状态、协议确认记录和设备会话的最小字段集
- [x] 明确 refresh token 的持久化形式，避免明文落库

## 3. `prisma/` 与运行时接线

- [x] 在 `prisma/schema.prisma` 中补齐 auth 相关模型
- [x] 生成并整理对应 migration
- [x] 在 `apps/api/src/modules/auth` 中补最小领域骨架或 repository 接线，供后续 step 复用

## 4. 验证与测试

- [x] 为 schema 映射、状态枚举或会话数据访问补单元测试或等价验证
- [x] 验证 migration 可以在本地开发环境下稳定执行
- [x] 验证后续 step 可以围绕这些模型继续扩展，而不必再次拆主表

## 5. 文档与注释

- [x] 如 auth 数据模型改变了开发者理解入口，更新 `prisma/README.md` 或等价模块说明
- [x] 对协议确认与会话模型中的非直观字段补必要注释

### 手动验收步骤

1. 执行数据库迁移并确认新表 / 新字段创建成功
2. 检查 `User`、协议确认记录和会话模型的关系是否能表达 auth spec 所需边界
3. 确认 schema 中没有把 token 明文或不必要的业务细节直接塞进模型
