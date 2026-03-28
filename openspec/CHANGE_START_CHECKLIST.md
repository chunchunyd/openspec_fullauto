# 新 Change 开始前检查清单

本清单用于在创建任何新的 `openspec/changes/<change-id>/` 之前，先完成一次最小但必要的范围与前置条件检查，避免把共享层缺口、测试缺口、文档缺口或过大的实施范围直接带进业务 change。

## 1. 先对齐现有真相源

- [ ] 确认本次工作对应的 capability，并先阅读现有 `openspec/specs/<capability>/spec.md`
- [ ] 如果发现现有 spec 与当前仓库目录、应用命名、共享层命名或运行时边界明显不一致，先修正真相源，再继续创建新 change
- [ ] 如果本次是返工、重构或补洞，确认是否已有旧 change；有的话，新开 change，不直接继续沿用旧 change 作为当前实施计划
- [ ] 如果本次变更跨多个 capability，先判断是否真的需要放在同一个 change 中，还是应该拆成多个小 change
- [ ] 如果现有 spec 还停留在 delta 形态、早期蓝图或明显目标态描述，先收敛为当前 spec 再作为后续输入

## 2. 检查是否依赖共享层

- [ ] 列出本次 change 依赖的共享运行时服务：例如 `libs/database`、`libs/cache`、`libs/sms`、`libs/observability`、`libs/queue`、`libs/storage`
- [ ] 列出本次 change 依赖的共享契约产物：例如 `packages/api_contracts`、事件 schema、任务契约、共享配置 schema
- [ ] 明确这些依赖属于 `libs/` 还是 `packages/`，不要混层

### 判断规则

- `libs/`：运行时共享服务、module、port、adapter、utility、供应商接线
- `packages/`：跨运行时共享契约，例如 API contract、事件 schema、job payload schema、共享配置 schema

## 3. 检查共享层是否真的可复用

- [ ] 对每个依赖的 `libs/` / `packages/` 检查是否已有实际实现，而不是空目录、空文件或只有命名占位
- [ ] 检查是否已经有公开入口、README 或等价模块说明
- [ ] 检查当前 app 是否已经能以稳定方式导入和使用该共享层
- [ ] 如果共享层未完成，决定是：
- [ ] 先拆一个前置小 change 补齐共享层
- [ ] 或者把补齐共享层显式纳入当前 change 的 proposal、design、tasks
- [ ] 不允许默认在业务模块内临时复制一套共享能力长期使用

## 4. 收紧 change 粒度

- [ ] 尽量把范围控制在一个 app 的单一子能力内
- [ ] 如果同时涉及多个 app、多个运行时或多个明显独立的 workstream，优先拆成多个 change
- [ ] 如果同一能力有明显先后顺序，change id 使用 `step-01`、`step-02` 这类顺序标记
- [ ] 如果这个 change 同时还要补共享基础设施，确认是否已经大到应该拆分

## 5. 提前想清日志与可观测性

- [ ] 标出本次主流程中的关键开始、成功、失败、降级、重试节点
- [ ] 判断是否依赖 `libs/observability` 或其他共享日志接线
- [ ] 如果 change 同时涉及服务端和 mobile，分别说明两侧日志方案，不默认共用同一套实现
- [ ] 如果日志基础设施本身还没成型，优先拆前置 change，或在当前 change 中明确补齐范围

## 6. 提前写测试计划

- [ ] 在创建 change 时就写出测试计划，而不是等实现快结束再补
- [ ] 后端纯逻辑、策略、校验、映射优先单元测试
- [ ] 后端接口、数据库读写、权限控制、多组件协作优先集成测试或等价验证
- [ ] mobile 状态管理、纯函数与 service 层优先单元测试；关键页面流程优先 widget 测试或等价验证
- [ ] 如果会新增或修改自动化测试文件，提前约定这些测试文件的头注释要写明完整执行指令
- [ ] 如果暂时不适合补自动化测试，写明原因，并保留可重复执行的手动验收步骤

## 7 如果同时涉及 API 与前端

- [ ] 判断本次 change 是否同时涉及 API 后端与 `mobile` 或 `admin-web`
- [ ] 如果同时涉及，先明确共享 HTTP contract 影响范围
- [ ] 将“稳定 API contract”与执行 `openapi-export` 写入前置任务，再安排前端正式接入
- [ ] 确认前端字段依据是最近一次导出的共享契约，而不是长期沿用口头约定

## 8. 提前确认注释、文档与 README 义务

- [ ] 如果会引入非直观逻辑、状态机、协议适配、缓存/队列语义、安全边界或复杂容错，任务里显式加入必要注释或模块说明
- [ ] 如果会新增或实质修改 `libs/`、`packages/`，任务里显式加入对应 README 或等价模块文档更新
- [ ] 如果会改变开发命令、环境变量、目录结构、脚本入口、人工操作流程或共享层使用方式，任务里显式加入根 README 或相关入口文档更新
- [ ] 把注释、模块文档、README 更新视为正式交付内容，不作为可省略的收尾项

## 9. 形成 change 产物

- [ ] `proposal.md` 写清：为什么做、包含什么、不包含什么、预期结果、影响范围
- [ ] `design.md` 在跨模块边界、状态机、共享层取舍不直观时补上
- [ ] `tasks.md` 按 workstream 分组，并把共享层检查、日志、测试、文档更新写成明确任务
- [ ] `tasks.md` 中只有可执行动作使用 checkbox；人工职责、范围排除和“本 change 不执行”的说明改用普通项目符号或备注
- [ ] `tasks.md` 的验收 / 验证部分已显式加入 ESLint 验收和 TypeScript 验收，并分别参考主仓库 `docs/eslint-style-notes.md` 与 `docs/tsc-fix-summary.md`；如果当前 change 不适用其中某项，已在任务中写明原因
- [ ] 如果 `tasks.md` 中出现 `commit`、`提交`、`阶段性提交`、`交接前收口提交` 或等价任务，相关任务文本已显式引用 `openspec/docs/git-commit-guidelines.md`
- [ ] 如果当前 change 属于 `xxx-step-xx-*` 系列，`tasks.md` 头部已使用固定自动化模板：`自动化确认系列集成分支 ... 已就绪` 与 `自动化从 ... 切出 <implementation-branch> 实现分支`
- [ ] 如果当前 change 属于 `xxx-step-xx-*` 系列，`tasks.md` 结尾已使用固定自动化模板：`自动化将 <implementation-branch> merge 回 series/<series-prefix>，保留实现分支上的阶段性提交历史`；`series/<series-prefix> -> dev` 由人工执行写成普通备注
- [ ] 如果同一系列的全部 change 都已生成，已在 `openspec/auto/deps/` 下补 `deps.<series-prefix>.json`
- [ ] 如果计划让多个 series 一起通过 `auto_apply.sh` 执行，已确认它们彼此独立、不会在依赖图中交叉引用
- [ ] 如果多个 workstream 实际围绕同一个目标能力相互依赖，已在创建阶段直接合并成一个以目标命名的 `series prefix`，而不是拆成多个交叉依赖的系列
- [ ] 如果修改既有 requirement，在 delta 中写完整更新后的 requirement 文本
- [ ] 确认 capability spec 只承载当前行为与稳定边界，不把提交流程、实施顺序或文档义务重新写回 spec

## 10. 实施前的分支与提交策略

- [ ] 从最新 `dev` 出发
- [ ] 如果当前 change 属于 `xxx-step-xx-*` 系列，先确认 `series/<series-prefix>` 已从最新 `dev` 切出或同步
- [ ] 如果当前 change 属于 `xxx-step-xx-*` 系列，从 `series/<series-prefix>` 切出 `feat/<change-id>`、`fix/<change-id>` 或 `chore/<change-id>`；否则再直接从最新 `dev` 切出实现分支
- [ ] 如果当前 change 属于 `xxx-step-xx-*` 系列，在切出实现分支前，不进行任何实现性编辑、代码生成、格式化、构建或可能写文件的测试动作
- [ ] 在第一处实现性编辑发生前，确认当前不在 `dev` / `main` 上，且分支名已包含本次 change id
- [ ] 如果当前 change 属于 `xxx-step-xx-*` 系列，在第一处实现性编辑发生前，确认当前也不在 detached `HEAD` 或 `series/<series-prefix>` 上
- [ ] 检查主项目工作树是否已存在与当前 change 无关的未提交改动；如果有，先暂停并整理边界，不要直接叠加开发
- [ ] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动；默认把它们视为当前 change 的继承现场，在其基础上继续或安全清理，不要直接忽略
- [ ] 实施过程中每完成一个或少数几个紧密相关 task，就及时 commit
- [ ] 不要在没有阶段性 commit 的情况下连续跨越多个 workstream；一个小段实现达到可运行、可验证或可回退状态后就提交
- [ ] 如果发现自己已经误在 `dev` 上开始开发，立即停止继续堆改动，先切出对应分支，再恢复后续实现
- [ ] 如果发现自己已经误在 detached `HEAD` 或 `series/<series-prefix>` 上开始系列 step 开发，立即停止继续堆改动，先切出对应实现分支，再恢复后续实现
- [ ] 如果当前 change 属于 `xxx-step-xx-*` 系列，在切回或合并回 `series/<series-prefix>` 前，确认实现分支上的有效改动已经全部提交，且工作区保持干净
- [ ] 如果当前 change 属于 `xxx-step-xx-*` 系列，整个 step 完成并自检后再合并回 `series/<series-prefix>`
- [ ] `series/<series-prefix> -> dev` 的系列收口由人工执行，不作为 agent 默认任务
- [ ] 非系列 change 在完成并自检后再合并回 `dev`
- [ ] `dev -> main` 的发布合并不在 AI 默认职责内，由人工执行

## 11. 建议的最终自问

- [ ] 这个 change 是否仍然足够小，能在一次评审中看清楚？
- [ ] 这个 change 是否只承载一个主目标，而不是把多个并列主产物塞进同一个标题？
- [ ] 我是不是在业务模块里偷偷复制了本应属于共享层的能力？
- [ ] 我是不是把目标蓝图、长期预留或想象中的实现状态写成了当前 spec？
- [ ] 我是不是把流程治理或协作顺序误写进了 capability spec？
- [ ] 测试、日志、注释和 README 更新是否已经进入 tasks，而不是停留在口头上？
- [ ] 如果未来另一个 agent 接手，它能否只看 OpenSpec 和仓库文档就继续推进？
