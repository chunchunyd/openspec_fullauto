# Delta for Analytics

## ADDED Requirements

### Requirement: 系统必须让原始分析事件存储锚点成为可部署的正式 schema

系统必须让原始分析事件存储锚点成为可部署的正式 schema，以保证新环境能够通过版本化迁移建立与当前实现一致的原始事件存储结构。 The system MUST make the raw analytics event storage anchor deployable through versioned schema migration.

#### Scenario: 初始化一个新环境

- WHEN 一个新环境按正式数据库迁移流程初始化 analytics 存储
- THEN 系统必须能够建立当前承诺的原始事件表、唯一约束和必要索引
- AND 不得要求人工手写表结构或依赖隐式历史状态

#### Scenario: 运行时与测试读取 analytics schema

- WHEN runtime 或测试通过生成后的 Prisma contract 读取 analytics 模型
- THEN 它们必须看到与当前 schema 一致的枚举和模型定义
- AND 不得继续依赖过期或手工继承的 generated artifact
