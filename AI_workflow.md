# AI Workflow 草案

本文档定义基于 OpenSpec 的全自动工作流草案。

目标不是替代 OpenSpec，而是在不破坏 `openspec/` 真相源边界的前提下，为需求拆解、change 生成、并行实现、验收、复盘和知识沉淀提供一套可自动运行的控制层。

## 1. 目标

工作流需要满足以下目标：

- 在 `openspec/changes/*` 已创建后，能够按依赖关系并行推进实现。
- 能自动选择合适的 Agent 承担不同类型任务。
- 能在多轮实现后自动进入验收，并根据验收结果继续生成修复型 change。
- 能把项目经验沉淀为稳定 guidance，而不是只留在一次性对话或日志里。
- 能在 API 限流、任务不完整、merge 冲突、验收失败等情况下稳定收敛，而不是失控。

## 2. 基本原则

### 2.1 真相源原则

以下边界必须严格固定：

- `openspec/specs/*`
  - 当前系统能力和行为的真相源。
- `openspec/changes/*`
  - 当前活跃 change 的唯一真相源。
- `openspec/changes/archive/*`
  - 已归档 change 的真相源。
- `openspec/project.md`
  - 项目级 OpenSpec 设计约束。
- `openspec/config.yaml`
  - OpenSpec 工具配置。

自动化层绝不能把这些真相源复制成第二份“状态真相”。

### 2.2 控制层原则

未来新增的 `openspec_autosteer/` 是控制层，不是真相层。

它只负责：

- 需求、架构、约束文档
- 调度索引
- Agent 能力配置
- 运行期审计信息
- 验收报告
- 指导文档

它不负责声明“某个 change 是否真正完成”。这一判断必须始终从 `openspec/changes/*`、`tasks.md`、归档状态和执行结果派生。

### 2.3 执行器原则

`openspec_py/` 是执行层。

它负责：

- 扫描 workspace
- 构造计划
- 启动执行
- 准备 worktree
- 驱动验证、归档和 merge
- 记录运行事件

它不负责长期保存项目知识，也不直接承担需求规划真相源。

## 3. 分层结构

整体分为三层：

### 3.1 真相层

- `openspec/`

### 3.2 控制层

- `openspec_autosteer/`

### 3.3 执行层

- `openspec_py/`

推荐关系：

- 控制层读取真相层，生成调度输入。
- 执行层读取真相层和控制层，执行工作流。
- 执行结果回写真相层允许的状态位置，例如 OpenSpec change、归档、兼容 `.result`。
- 控制层只记录索引、建议、审计和知识，不回写“第二份真相”。

## 4. `openspec_autosteer/` 目录规划

未来建议建立如下目录：

```text
openspec_autosteer/
  docs/
  guidance/
  reviews/
  regulations/
  feed/
  registry/
  runtime/
  prompts/
  scripts/
```

各目录职责如下。

### 4.1 `docs/`

作为自动化控制层的文档真相源。

放置内容：

- 需求文档
- 架构设计文档
- 模块边界说明
- 非 OpenSpec 结构化规划文档

这里是调度 Agent 的主要业务输入来源。

### 4.2 `guidance/`

用于存放项目级可复用指导。

例如：

- 代码风格要求
- ESLint 处理规范
- TypeScript 报错处理规范
- Prisma 特殊问题处理规范
- 测试修复惯例
- 前端 UI/交互约束

所有实现 Agent 在进入“验证与测试”阶段时，必须参考相关 guidance。

只有“可复用、可判定、可迁移”的经验，才应该写入这里。

建议每条 guidance 至少包含：

- 症状
- 触发条件
- 推荐处理
- 禁止处理
- 适用范围

### 4.3 `reviews/`

存放验收和 review 报告。

例如：

- change 验收报告
- 批次验收报告
- 系列回归报告
- 架构一致性检查报告

开发 Agent 在后续修复时，应参考历史 review，避免同类问题反复横跳。

### 4.4 `regulations/`

存放区别于 OpenSpec 官方默认规则的本项目自定义规则。

内容来源可以包括：

- 当前的 OpenSpec 本地扩展规则
- 系列 change 管理规则
- branch / merge 管理规则
- 自动化流程附加约束

可以视为“本项目 OpenSpec 方言层”。

### 4.5 `feed/`

存放用户实时输入的控制指令。

但这里不建议使用“发现新内容立即热修改”的语义。

推荐语义是：

- 调度循环每一轮开始前检查 `feed/`
- 若发现新指令，则进入控制收敛点
- 调度器判断本轮应该：
  - `continue`
  - `replan`
  - `stop`

也就是说，`feed/` 是“运行时控制输入”，不是“立即中断并现场改文件”的热补丁入口。

### 4.6 `registry/`

存放稳定配置数据。

建议包括：

- `agent_list.json`
  - Agent 静态能力画像
- 其他静态注册表
  - 任务类型标签
  - 验收类型标签
  - prompt 模板索引

### 4.7 `runtime/`

存放运行期派生数据。

建议包括：

- `proposals.json`
  - proposal 索引
- `change_index.json`
  - proposal 与 change_id 映射
- `agent_scores.json`
  - Agent 动态评分
- `run_state.json`
  - 当前调度轮次状态
- 审计型事件记录

这里可以记录状态，但这些状态都必须是“派生状态”，不是最终真相。

### 4.8 `prompts/`

存放基础 prompt 模板。

例如：

- 调度 Agent prompt
- 实现 Agent prompt
- 验收 Agent prompt
- review Agent prompt
- guidance 更新 prompt

通过 OpenSpec 动态生成的 instructions 不放这里。

### 4.9 `scripts/`

存放控制层脚本。

例如：

- 调度脚本
- Git 辅助脚本
- 数据整理脚本
- Agent 评分更新脚本

建议把主脚本拆成多个 Python 模块维护，而不是继续堆到单个超长 shell 里。

## 5. Agent 体系设计

在后续架构中，必须区分 `agent` 与 `runner`。

- `agent`
  - 表示能力画像、适用范围、历史表现。
- `runner`
  - 表示实际执行任务的命令行环境与适配器。

这样做的原因是：你当前同时使用 Claude Code 和 Codex，它们不是“只换模型名”的关系，而是两套不同的 CLI 运行时。

因此架构不能写成“支持某几个模型”，而要写成“支持多种 runner”。

## 5.1 Agent 静态注册

建议通过 `openspec_autosteer/registry/agent_list.json` 管理。

每个 Agent 至少声明：

- `id`
- `model`
- `vendor`
- `runner_type`
- `strengths`
- `weaknesses`
- `cost_level`
- `speed_level`
- `tooling_capabilities`
- `preferred_task_types`
- `forbidden_task_types`

例如：

- 前端实现强
- 重构强
- 逻辑实现强
- 验收强
- 文档整理强

### 5.2 Agent 动态评分

建议另建 `openspec_autosteer/runtime/agent_scores.json`。

动态评分应与静态注册分开。

推荐维度：

- 任务完成率
- 一次完成率
- 平均重试次数
- 人工接管率
- 测试通过率
- 前端实现满意度
- review 发现问题密度
- 回归引入率

调度时先基于静态能力过滤，再基于动态评分排序。

### 5.3 Agent 角色

建议至少区分四类角色：

- 调度 Agent
  - 负责拆 proposal、设计依赖、分配任务、决定进入验收。
- 实现 Agent
  - 负责具体 change 的编码、测试、同步 `tasks.md`。
- 验收 Agent
  - 负责独立验收，不参与当前实现。
- 复盘 Agent
  - 负责把通用经验沉淀进 `guidance/`，把项目性问题归档进 `reviews/`。

## 5.4 Runner 适配层

必须显式设计 Runner 适配层。

调度器不应直接依赖：

- `claude`
- `codex`
- `opsx`
- 任何具体 CLI 命令

而应通过统一 runner 接口调用。

推荐每种 CLI 各自实现一个 adapter。

首批建议支持：

- `claude_code`
  - 对应 Claude Code CLI
- `codex_cli`
  - 对应 Codex CLI

未来可扩展：

- `gemini_cli`
- `custom_shell_runner`
- `remote_agent_runner`

### 5.5 Runner 注册信息

建议在 `openspec_autosteer/registry/` 中新增 runner 注册表，例如：

- `runner_list.json`

每个 runner 至少声明：

- `runner_type`
- `command`
- `vendor`
- `environment_requirements`
- `supports_tools`
- `supports_multiline_prompt`
- `supports_streaming`
- `supports_resume`
- `rate_limit_strategy`
- `output_parser`

### 5.6 Runner 负责的内容

每个 runner adapter 负责：

- 命令拼装
- prompt 注入方式
- 工作目录切换
- 输出采集
- 成功/失败判定
- 限流错误识别
- 重试策略
- 中断与恢复策略

调度器不处理这些 CLI 差异。

### 5.7 调度器只看统一协议

调度器与 runner 之间只通过统一任务协议交互。

调度器只关心：

- 任务类型
- 所需能力标签
- 目标工作目录
- 允许的工具范围
- 超时时间
- runner 返回状态

它不应该关心底层是 Claude 还是 Codex。

### 5.8 为什么必须拆分 Agent 与 Runner

因为同一个 Agent 画像未来可能绑定不同 runner。

例如：

- 一个“前端实现强”的 agent
  - 可以先绑定 `codex_cli`
  - 后续也可能切到别的 runner

而同一个 runner 也可能承载多个 Agent 画像：

- `codex_cli`
  - 前端实现 agent
  - 重构 agent
  - review agent

如果不拆开，后面会把“能力选择”和“命令执行”耦合死。

## 6. Proposal 与 Change 跟踪设计

不建议只保留一个 `changes_list.json`。

建议拆为两个派生索引。

### 6.1 `proposals.json`

记录 proposal 级信息：

- proposal_id
- 生成时间
- 来源轮次
- 需求来源
- proposal 摘要
- 建议依赖
- 优先级
- 当前阶段

### 6.2 `change_index.json`

记录 proposal 与真实 OpenSpec change 的映射：

- proposal_id
- change_id
- 创建时间
- 当前轮次
- 是否已归档

### 6.3 状态边界

这些索引中不应存放最终状态真相。

例如以下字段只能是派生字段，不应成为控制决策的唯一依据：

- `done`
- `passed`
- `archived`
- `blocked`

真正判断时仍要回读：

- `openspec/changes/<change-id>/`
- `tasks.md`
- `openspec/changes/archive/`
- 运行结果文件

## 7. 调度工作流

推荐采用双环流程，而不是单环自洽流程。

### 7.1 开发环

步骤如下：

1. 调度 Agent 读取：
   - `openspec/`
   - `openspec_autosteer/docs/`
   - `openspec_autosteer/guidance/`
   - 历史 `reviews/`
2. 生成细粒度 proposal 集合。
3. 设计 proposal 间依赖关系。
4. 通过受控 OpenSpec 接口创建 change。
5. 将 proposal 与 change_id 回填到索引。
6. 调度实现 Agent 并行执行 change。
7. 所有 change 完成后，进入验收环。

### 7.2 验收环

步骤如下：

1. 独立验收 Agent 读取：
   - 当前代码实现
   - 当前 OpenSpec 状态
   - 历史 review 报告
   - 历史 guidance
2. 生成验收报告。
3. 判断结果：
   - 通过
   - 进入修复 proposal
   - 更新 guidance
   - 请求人工确认

### 7.3 为什么必须双环

如果让同一个 Agent 同时负责：

- proposal 设计
- 实现
- 最终验收

那么它会天然偏向于“为自己辩护”，而不是严格验收。

因此最终验收必须由独立角色承担。

## 8. OpenSpec 接口策略

不要把未来架构绑死在某一个交互工具上，例如 `opsx`。

建议抽象一个 OpenSpec adapter，统一提供这些能力：

- `create_proposal`
- `create_change`
- `apply_change`
- `validate_change`
- `archive_change`
- `read_status`

底层可以是：

- `opsx:*`
- OpenSpec CLI
- 后续封装的 Python 接口

上层调度器不应直接依赖某一种工具交互形态。

同理，也应抽象一个 Runner adapter，统一提供这些能力：

- `run_task`
- `resume_task`
- `cancel_task`
- `collect_output`
- `classify_error`
- `detect_rate_limit`

## 9. 与当前 `openspec_py` 的关系

当前 `openspec_py/` 已经具备以下执行层能力：

- 状态扫描
- 计划构建
- launch 执行
- retry / assessment
- finalize
- merge queue
- 主循环 `run`
- 兼容旧 session 恢复

因此未来建议分工如下：

- `openspec_autosteer/`
  - 决定“做什么”
- `openspec_py/`
  - 负责“怎么执行”

也就是说，控制层产出 proposal、调度配置、Agent 选择和验收结论；
执行层负责把这些计划落实到 workspace。

后续 `openspec_py/` 中的执行器应继续向“runner adapter 化”演进。

推荐未来演进方向：

- 调度层输出：
  - `agent_id`
  - `runner_type`
  - `task payload`
- 执行层根据 `runner_type` 选择实际 adapter
  - `ClaudeCodeRunner`
  - `CodexRunner`

这样才能自然支持多 CLI 混用。

## 10. 错误处理原则

### 10.1 API 限流

这是必须重点处理的错误类型。

要求：

- 所有模型调用都必须有重试策略
- 必须区分“可重试错误”和“不可重试错误”
- 必须有指数退避
- 必须有最大重试次数
- 超限后必须进入明确状态：
  - `retry_later`
  - `needs_human`
  - `halted`

### 10.2 不完整实现

若 change 执行后 `tasks.md` 仍不完整：

- 先执行 task sync
- 再执行 assessment
- 再决定 retry 或人工介入

### 10.3 Merge 冲突

若系列 merge 失败：

- 先进入 merge fallback
- 若 fallback 后仍未完成
  - 标记 `needs_human`
  - 保留现场
  - 输出明确恢复路径

### 10.4 验收失败

若验收失败：

- 优先生成修复型 proposal
- 必要时升级 guidance
- 避免直接回到原实现 Agent 自由发挥

## 11. 必须固化的规则

后续实现时建议把下面这些规则作为硬规则写入规约。

### 11.1 单一真相源规则

`openspec/changes/*` 永远是真相源。

### 11.2 控制层不越权规则

调度 Agent 不直接手写 OpenSpec 真相状态，只通过受控接口创建和推进 change。

### 11.3 验收独立规则

实现 Agent 不能充当最终验收 Agent。

### 11.4 Guidance 准入规则

只有通用且稳定的处理方式才能写入 `guidance/`。

### 11.5 Feed 收敛规则

`feed/` 的新指令只能在调度收敛点处理，不做无条件热修改。

## 12. 第一阶段落地建议

建议先按最小闭环落地，而不是一次做全。

第一阶段只做：

1. 建立 `openspec_autosteer/` 目录骨架。
2. 明确 `agent_list.json`、`runner_list.json` 和 `agent_scores.json` 结构。
3. 明确 `proposals.json` 和 `change_index.json` 结构。
4. 先实现统一 runner 协议，首批只接：
   - `claude_code`
   - `codex_cli`
5. 先由调度 Agent 只负责生成 proposal 和依赖，不直接实现。
6. 继续用 `openspec_py run` 作为执行器。
7. 单独实现验收环，不和开发环混用。

## 13. 暂定结论

本草案采纳以下核心方向：

- 保留 OpenSpec 为真相层
- 新建 `openspec_autosteer/` 作为控制层
- 使用 `openspec_py/` 作为执行层
- 使用 `agent` 与 `runner` 分离的多 CLI 架构
- 采用“开发环 + 验收环”的双环架构
- 使用静态 Agent 注册 + 动态评分
- 使用 proposal 索引 + change 映射，而不是第二份状态真相
- 把 API 限流、merge 冲突、不完整实现视为一等公民错误场景

后续若要继续推进，下一步应先补一份“数据结构定义文档”，明确：

- `agent_list.json`
- `runner_list.json`
- `agent_scores.json`
- `proposals.json`
- `change_index.json`
- `feed/` 文件格式
