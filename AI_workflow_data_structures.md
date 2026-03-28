# AI Workflow 数据结构设计 V1

本文档定义 `openspec_autosteer/` 控制层的首批核心数据结构。

目标是先给未来实现提供稳定边界，而不是一步到位覆盖所有字段。

本设计遵循以下原则：

- `openspec/` 仍然是真相层
- `openspec_autosteer/` 只保存控制层和派生层数据
- `openspec_py/` 负责执行，不负责长期控制层知识
- `agent` 与 `runner` 分离

## 1. 目录映射

首批建议对应如下文件：

```text
openspec_autosteer/
  registry/
    agent_list.json
    runner_list.json
  runtime/
    agent_scores.json
    proposals.json
    change_index.json
    run_state.json
  feed/
    *.json
```

## 2. 通用约定

### 2.1 ID 约定

- `agent_id`
  - 稳定字符串 ID，例如 `codex-frontend-primary`
- `runner_type`
  - runner 类型 ID，例如 `codex_cli`
- `proposal_id`
  - proposal 稳定 ID，例如 `prop-20260328-001`
- `run_id`
  - 一次调度主循环的运行 ID
- `acceptance_id`
  - 一次验收批次 ID

### 2.2 时间格式

统一使用 ISO 8601 字符串，例如：

```json
"2026-03-28T12:30:00+08:00"
```

### 2.3 枚举风格

统一使用小写蛇形或小写短横线风格，不混用中文枚举值。

例如：

- `active`
- `needs_human`
- `ready_for_merge`

## 3. `agent_list.json`

用途：

- 定义 Agent 静态能力画像
- 给调度器提供“能做什么”的筛选依据

位置：

- `openspec_autosteer/registry/agent_list.json`

建议结构：

```json
{
  "version": 1,
  "agents": [
    {
      "agent_id": "codex-frontend-primary",
      "label": "Codex Frontend Primary",
      "model": "gpt-5.4",
      "vendor": "openai",
      "runner_type": "codex_cli",
      "enabled": true,
      "priority": 100,
      "strengths": ["frontend_ui", "react", "refactor"],
      "weaknesses": ["long_running_acceptance"],
      "preferred_task_types": ["implement", "refine", "ui_fix"],
      "forbidden_task_types": ["final_acceptance"],
      "tooling_capabilities": ["shell", "git", "workspace_edit"],
      "cost_level": "high",
      "speed_level": "medium",
      "context_window_level": "high",
      "notes": "Preferred for React UI and codebase-wide refactors."
    }
  ]
}
```

字段建议：

- `version`
  - 配置版本
- `agents`
  - Agent 列表
- `agent_id`
  - 唯一 ID
- `label`
  - 人类可读名称
- `model`
  - 模型标识
- `vendor`
  - 提供方
- `runner_type`
  - 绑定哪个 runner
- `enabled`
  - 是否允许调度
- `priority`
  - 同等条件下的基础优先级
- `strengths`
  - 能力标签
- `weaknesses`
  - 弱项标签
- `preferred_task_types`
  - 优先承担的任务类型
- `forbidden_task_types`
  - 禁止分配的任务类型
- `tooling_capabilities`
  - 可使用工具集合
- `cost_level`
  - `low | medium | high`
- `speed_level`
  - `low | medium | high`
- `context_window_level`
  - `low | medium | high`
- `notes`
  - 备注

## 4. `runner_list.json`

用途：

- 定义实际执行任务的 CLI 运行时
- 屏蔽 Claude Code、Codex 等执行差异

位置：

- `openspec_autosteer/registry/runner_list.json`

建议结构：

```json
{
  "version": 1,
  "runners": [
    {
      "runner_type": "codex_cli",
      "label": "Codex CLI",
      "vendor": "openai",
      "enabled": true,
      "command": "codex",
      "args_template": [],
      "environment_requirements": ["CODEX_HOME"],
      "supports_tools": true,
      "supports_multiline_prompt": true,
      "supports_streaming": true,
      "supports_resume": false,
      "rate_limit_strategy": "provider_retry",
      "output_parser": "codex_v1",
      "error_classifier": "codex_v1",
      "notes": "Primary runner for Codex-based implementation agents."
    },
    {
      "runner_type": "claude_code",
      "label": "Claude Code",
      "vendor": "anthropic",
      "enabled": true,
      "command": "claude",
      "args_template": [],
      "environment_requirements": [],
      "supports_tools": true,
      "supports_multiline_prompt": true,
      "supports_streaming": true,
      "supports_resume": false,
      "rate_limit_strategy": "provider_retry",
      "output_parser": "claude_code_v1",
      "error_classifier": "claude_code_v1",
      "notes": "Primary runner for Claude Code-based implementation agents."
    }
  ]
}
```

字段建议：

- `runner_type`
  - runner 唯一类型名
- `label`
  - 人类可读名称
- `vendor`
  - 提供方
- `enabled`
  - 是否允许使用
- `command`
  - 本地命令名
- `args_template`
  - 默认参数模板
- `environment_requirements`
  - 所需环境变量或依赖
- `supports_tools`
  - 是否支持工具能力
- `supports_multiline_prompt`
  - 是否适合长 prompt
- `supports_streaming`
  - 是否支持流式输出
- `supports_resume`
  - 是否支持会话恢复
- `rate_limit_strategy`
  - 限流恢复策略名
- `output_parser`
  - 输出解析器名
- `error_classifier`
  - 错误分类器名
- `notes`
  - 备注

## 5. `agent_scores.json`

用途：

- 保存 Agent 动态表现
- 作为调度排序的重要参考

位置：

- `openspec_autosteer/runtime/agent_scores.json`

建议结构：

```json
{
  "version": 1,
  "updated_at": "2026-03-28T12:30:00+08:00",
  "agents": [
    {
      "agent_id": "codex-frontend-primary",
      "score": 0.86,
      "confidence": 0.72,
      "samples": 18,
      "metrics": {
        "completion_rate": 0.89,
        "first_pass_rate": 0.61,
        "retry_rate": 0.22,
        "needs_human_rate": 0.11,
        "test_pass_rate": 0.83,
        "review_findings_per_task": 0.44,
        "regression_rate": 0.06
      },
      "task_type_scores": {
        "implement": 0.9,
        "ui_fix": 0.94,
        "acceptance": 0.58
      },
      "tag_scores": {
        "frontend_ui": 0.95,
        "react": 0.91,
        "prisma": 0.56
      },
      "notes": "Strong on UI delivery, weaker on backend edge cases."
    }
  ]
}
```

字段建议：

- `score`
  - 综合得分，`0 ~ 1`
- `confidence`
  - 当前评分可信度
- `samples`
  - 样本数量
- `metrics`
  - 基础统计指标
- `task_type_scores`
  - 按任务类型拆分的得分
- `tag_scores`
  - 按标签拆分的得分

## 6. `proposals.json`

用途：

- 保存 proposal 层索引
- 记录“为什么产生这个 change 候选”

位置：

- `openspec_autosteer/runtime/proposals.json`

建议结构：

```json
{
  "version": 1,
  "updated_at": "2026-03-28T12:30:00+08:00",
  "proposals": [
    {
      "proposal_id": "prop-20260328-001",
      "title": "Harden self endpoint validation",
      "summary": "Strengthen request validation for self endpoints and align error handling.",
      "source_type": "planner",
      "source_run_id": "run-20260328-001",
      "phase": "development",
      "status": "converted_to_change",
      "priority": "high",
      "capability_tags": ["users", "api", "validation"],
      "depends_on": ["prop-20260328-000"],
      "acceptance_required": true,
      "created_at": "2026-03-28T12:00:00+08:00",
      "updated_at": "2026-03-28T12:10:00+08:00"
    }
  ]
}
```

字段建议：

- `proposal_id`
  - proposal 唯一 ID
- `title`
  - 标题
- `summary`
  - 简要描述
- `source_type`
  - 来源，例如 `planner | acceptance | human | review`
- `source_run_id`
  - 来源运行 ID
- `phase`
  - `development | acceptance | remediation`
- `status`
  - `draft | approved | converted_to_change | dropped`
- `priority`
  - `low | medium | high | critical`
- `capability_tags`
  - 能力标签
- `depends_on`
  - proposal 级依赖
- `acceptance_required`
  - 是否必须进入独立验收

## 7. `change_index.json`

用途：

- 建立 proposal 与 OpenSpec change 的映射
- 作为控制层检索入口

位置：

- `openspec_autosteer/runtime/change_index.json`

建议结构：

```json
{
  "version": 1,
  "updated_at": "2026-03-28T12:30:00+08:00",
  "items": [
    {
      "proposal_id": "prop-20260328-001",
      "change_id": "users-part1-step-05-self-endpoints-request-validation-hardening",
      "series": "users-part1",
      "step": 5,
      "phase": "development",
      "derived_status": "in_progress",
      "created_at": "2026-03-28T12:10:00+08:00",
      "updated_at": "2026-03-28T12:30:00+08:00",
      "last_run_id": "run-20260328-002",
      "last_acceptance_id": null,
      "notes": ""
    }
  ]
}
```

重要说明：

- `derived_status` 只是派生状态，不能当真相。
- 真正状态必须回读 `openspec/changes/*` 和运行结果。

字段建议：

- `proposal_id`
  - 对应 proposal
- `change_id`
  - 对应真实 OpenSpec change
- `series`
  - 所属系列
- `step`
  - step 编号
- `phase`
  - 当前所处环节
- `derived_status`
  - 派生状态
- `last_run_id`
  - 最近一次参与的调度运行
- `last_acceptance_id`
  - 最近一次验收批次

## 8. `run_state.json`

用途：

- 保存控制层当前调度主循环状态
- 方便恢复与观测

位置：

- `openspec_autosteer/runtime/run_state.json`

建议结构：

```json
{
  "version": 1,
  "run_id": "run-20260328-002",
  "mode": "development",
  "status": "running",
  "series_scope": ["users-part1"],
  "change_scope": [],
  "current_stage": "launch",
  "selected_agents": [
    {
      "agent_id": "codex-frontend-primary",
      "runner_type": "codex_cli",
      "task_type": "implement"
    }
  ],
  "started_at": "2026-03-28T12:20:00+08:00",
  "updated_at": "2026-03-28T12:21:30+08:00",
  "last_message": "launch batch running",
  "linked_runtime_files": {
    "openspec_py_latest_run": "openspec_py/runtime/latest-run.json"
  }
}
```

字段建议：

- `run_id`
  - 当前运行 ID
- `mode`
  - `development | acceptance | remediation`
- `status`
  - `planned | running | sleeping | completed | failed | halted`
- `series_scope`
  - 当前覆盖的 series
- `change_scope`
  - 当前覆盖的 change
- `current_stage`
  - 所处阶段
- `selected_agents`
  - 当前实际分配到的 agent
- `linked_runtime_files`
  - 指向执行层产物

## 9. `feed/*.json`

用途：

- 让用户向运行中的系统注入控制指令

位置：

- `openspec_autosteer/feed/*.json`

建议每个 feed 文件一条指令，不共享大文件。

建议结构：

```json
{
  "version": 1,
  "feed_id": "feed-20260328-001",
  "created_at": "2026-03-28T12:40:00+08:00",
  "author": "human",
  "target": {
    "scope_type": "series",
    "scope_value": "users-part1"
  },
  "action": "replan",
  "priority": "high",
  "payload": {
    "message": "需要先补文档，再继续当前系列实现。",
    "update_docs": true,
    "update_guidance": false
  },
  "status": "pending"
}
```

字段建议：

- `feed_id`
  - 指令 ID
- `target`
  - 作用域
- `action`
  - `continue | stop | replan | update_docs | update_guidance`
- `priority`
  - 优先级
- `payload`
  - 动作参数
- `status`
  - `pending | consumed | rejected`

## 10. 调度任务协议

虽然首版可以先不落文件，但建议尽早明确内部任务协议。

调度层向执行层传递的任务对象建议至少包含：

```json
{
  "task_id": "task-20260328-001",
  "task_type": "implement",
  "phase": "development",
  "proposal_id": "prop-20260328-001",
  "change_id": "users-part1-step-05-self-endpoints-request-validation-hardening",
  "agent_id": "codex-frontend-primary",
  "runner_type": "codex_cli",
  "workspace_root": "E:\\workspace\\AIFlowWithOpenSpec",
  "worktree_path": "E:\\workspace\\.openspec-auto-worktrees\\AIFlowWithOpenSpec\\users-part1-step-05-self-endpoints-request-validation-hardening",
  "prompt_template_id": "implement-default-v1",
  "capability_tags": ["api", "validation"],
  "timeout_seconds": 3600
}
```

## 11. 首批实现范围建议

建议第一阶段只实现以下最小闭环：

1. `agent_list.json`
2. `runner_list.json`
3. `agent_scores.json`
4. `proposals.json`
5. `change_index.json`
6. `feed/*.json`
7. 调度层内部任务协议

其中最关键的是：

- 先把 `runner_type` 抽象出来
- 首批只支持：
  - `claude_code`
  - `codex_cli`

## 12. 暂定不做的内容

首版先不要做：

- 复杂的自动学习评分回写
- 多维权重自动调优
- 跨机器远程 runner
- 图数据库式 proposal 关系存储
- 过度细碎的事件格式

先保证结构稳定、边界清晰、可以手工维护和审计。

## 13. 暂定结论

V1 数据结构设计明确了：

- `agent` 与 `runner` 分离
- 控制层文件与真相层文件分离
- proposal 跟踪与 change 真相分离
- feed 作为控制输入，而不是热补丁
- 多 CLI 混用通过 `runner_type` 统一接入

后续如果继续推进，下一步最适合的是：

1. 基于本文档创建 `openspec_autosteer/` 目录骨架。
2. 先手写一版示例 JSON。
3. 再决定哪些结构先接入 `openspec_py`。
