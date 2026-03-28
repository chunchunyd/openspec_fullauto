# Delta for Repository Structure

## MODIFIED Requirements

### Requirement: 仓库必须让 Prisma schema 与已提交 migration 历史保持同步

系统必须让 `prisma/schema.prisma` 与仓库中已提交的 migration 历史保持同步，避免在关系型结构已经进入当前 schema 后仍缺失对应 migration，包括 users 自我资料宿主与设置宿主这类已经进入当前主线的数据结构。 The system MUST keep the Prisma schema and committed migration history aligned whenever relational structures change, including already-delivered users profile and settings hosts.

#### Scenario: 提交新的关系型结构

- WHEN 一个 change 在 `prisma/schema.prisma` 中新增或实质修改 enum、table、index、foreign key 或等价关系型结构
- THEN 仓库必须同时提交与之对应的 migration 历史
- AND 不得只依赖当前 schema 文件表达目标数据库状态

#### Scenario: 校验 schema 与 migration 是否漂移

- WHEN 贡献者对关系型结构完成一次 change 收口
- THEN 仓库必须能够通过 drift 校验确认当前 schema 与已提交 migration 历史一致
- AND 不得把存在明显漂移的状态视为可交付结果

#### Scenario: 新环境根据 migration 初始化数据库

- WHEN 新环境或 CI 仅根据仓库中已提交的 migration 初始化数据库
- THEN 结果必须能够重建当前 schema 中已经交付的 users 资料与设置结构
- AND 不得要求调用方人工根据 schema 文件补表、补列或补约束
