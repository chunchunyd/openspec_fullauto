# Delta for Repository Structure

## ADDED Requirements

### Requirement: 仓库必须为共享对象存储提供统一接入边界

系统必须将对象存储视为共享运行时基础设施，而不是由单一业务模块长期私有实现。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

其中：

- `libs/storage` 负责对象存储 port、provider adapter、访问结果抽象和本地替身能力
- 业务模块负责自身媒体语义、对象与业务实体的关联以及资源用途划分


#### Scenario: 业务能力接入对象存储

- WHEN `content`、`agents` 或其他业务能力需要处理图片、封面或文件对象
- THEN 它们必须通过 `libs/storage` 暴露的共享抽象接入
- AND 不应在单个业务模块内长期维护独立云存储 SDK 接线

#### Scenario: 业务模块管理媒体语义

- WHEN 某个业务模块需要区分帖子图片、帖子封面、头像或其他媒体资源
- THEN 这些资源用途与业务关联规则应保留在业务模块自身
- AND `libs/storage` 不应演化成收口所有业务媒体语义的全局目录
