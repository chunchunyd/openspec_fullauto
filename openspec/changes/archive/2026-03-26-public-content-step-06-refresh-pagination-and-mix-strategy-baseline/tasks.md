# 任务拆解：Public Content Step 06 刷新、分页与混排策略基线

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-06-refresh-pagination-and-mix-strategy-baseline` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/feed/spec.md`、默认首页 feed 与 Agent 切换实现
- [x] 确认当前 step 只建立刷新、分页和最小混排策略，不混入互动写入

## 2. 刷新与分页

- [x] 为首页 feed 定义受控刷新与分页输入，确保切换视角后的分页语义稳定
- [x] 明确首页空态、异常与重试入口的最小返回结果

## 3. 混排策略基线

- [x] 建立最小服务端混排策略或等价规则出口，避免客户端硬编码蓝色能量与红色能量比例
- [x] 明确该策略仍属于首期基线，不把复杂实验系统提前塞进本 step

## 4. 验证与测试

- [x] 为首页刷新、分页、切换后分页衔接、空态与最小混排输出补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-06-refresh-pagination-and-mix-strategy-baseline` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

