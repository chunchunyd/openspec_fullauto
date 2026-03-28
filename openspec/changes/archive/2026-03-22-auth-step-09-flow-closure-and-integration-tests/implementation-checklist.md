# Step 09 实施清单

这份清单是给当前开发机直接照着执行的。

目标不是“自由发挥”，而是用最小改动完成 `auth-step-09-flow-closure-and-integration-tests`。

## 0. 先遵守这些约束

- 仓库在 WSL 内，命令优先在 Linux 侧执行，不要混用 Windows `node.exe` / `pnpm.exe`
- 只改 `auth` 相关文件，不要顺手把全局 `main.ts`、其他模块或全站基建一起重构
- 这一步的目标是“auth 对外主路径更清晰、HTTP 边界更可信”，不是做新的大架构
- 每完成一个小段落就跑一次对应测试，不要攒一大堆改动最后一起排错

推荐命令风格：

```bash
cd /home/ccyd/workspace/nenggan
corepack pnpm --dir apps/api exec tsc -p tsconfig.json --noEmit
corepack pnpm --dir apps/api exec jest src/modules/auth --runInBand
```

如果要跑新增的 HTTP 集成测试，优先单独跑测试文件，不要一开始就跑全量。

## 1. 先读这些文件，再开始改

- `apps/api/src/modules/auth/auth.controller.ts`
- `apps/api/src/modules/auth/otp.service.ts`
- `apps/api/src/modules/auth/session.service.ts`
- `apps/api/src/modules/auth/cache/auth-cache.service.ts`
- `apps/api/src/modules/auth/__tests__/otp.service.spec.ts`
- `apps/api/src/modules/auth/__tests__/session.service.spec.ts`
- `apps/api/src/common/guards/__tests__/auth.guard.spec.ts`
- `apps/api/test/app.e2e-spec.ts`
- `openspec/changes/auth-step-09-flow-closure-and-integration-tests/proposal.md`
- `openspec/changes/auth-step-09-flow-closure-and-integration-tests/design.md`
- `openspec/changes/auth-step-09-flow-closure-and-integration-tests/tasks.md`

## 2. 建议按这 4 个小批次实施

### 批次 A：收敛公开 OTP 登录主路径

目标：公开主入口只保留 `/auth/login`。

建议改动：

- 先全仓 grep `'/auth/otp/verify'`
- 如果仓库内没有真实调用方，直接从 `AuthController` 移除这个公开路由
- 保留 `OtpService.verifyLoginOtp()`，因为 `/auth/login` 还要复用它
- 如果短期内不能删路由，至少不要再把它作为公开推荐登录入口：
  - Swagger summary / description 要明确“内部或兼容用途”
  - 不要让客户端文档继续暗示“先验码、后登录”是当前标准流程

优先推荐方案：

- `auth.controller.ts` 中直接移除 `@Post('otp/verify')` 对外入口
- 保留 service 层能力，不新增 exchange token 之类新机制

为什么这样做：

- 当前公开路由成功后会消耗 OTP，但没有公开后续会话交换步骤
- 继续保留会让前端或调用方误用

这一批完成后至少检查：

- `/auth/login` 仍是唯一公开 OTP 登录入口
- controller 编译通过
- OpenAPI 如有变化，后续要记得导出

### 批次 B：统一手机号 canonical format

目标：auth 内部统一使用 `11` 位大陆手机号，入口接受常见格式。

建议改动文件：

- `apps/api/src/modules/auth/cache/auth-cache.service.ts`
- `apps/api/src/modules/auth/cache/__tests__/auth-cache.service.spec.ts`
- `apps/api/src/modules/auth/__tests__/otp.service.spec.ts`
- 如有必要，`apps/api/src/modules/auth/__tests__/auth.repository.spec.ts`

推荐规则：

1. 先去掉所有非数字字符
2. 如果结果是 `13` 位且以 `86` 开头，去掉前导 `86`
3. 最终内部格式必须是 `11` 位大陆手机号，例如 `13800138000`
4. 短信发送时再拼 `+86`

建议实现形态：

```ts
normalizePhone(phone: string): string {
  const digits = phone.replace(/\D/g, '');
  if (digits.length === 13 && digits.startsWith('86')) {
    return digits.slice(2);
  }
  return digits;
}
```

注意事项：

- 不要把 `+86` 作为数据库、cache key、OTP 校验里的主格式
- 先 grep 当前测试和 fixture 里所有 `+86`，确认哪些只是旧测试写法，哪些真的是运行时约束
- 如果 repository 单测里还在用 `+8613800138000`，优先把测试和 auth 运行时真相对齐到 `13800138000`
- 如果你发现仓库里真的有依赖 `+86` 持久化格式的 seed / fixture / migration，再暂停汇报，不要静默改坏

这一批完成后至少补这些测试：

- `13800138000 -> 13800138000`
- `138 0013 8000 -> 13800138000`
- `138-0013-8000 -> 13800138000`
- `+86 138 0013 8000 -> 13800138000`
- 发送短信时仍是 `+8613800138000`

### 批次 C：细化 refresh token 错误语义

目标：至少区分 `REFRESH_TOKEN_EXPIRED` 和 `INVALID_REFRESH_TOKEN`。

建议改动文件：

- `apps/api/src/modules/auth/session.service.ts`
- `apps/api/src/modules/auth/__tests__/session.service.spec.ts`

推荐做法：

- 在 `refreshSession()` 的 `verifyAsync()` catch 分支里判断错误类型
- 如果是 JWT 过期，返回 `REFRESH_TOKEN_EXPIRED`
- 其他签名、格式、损坏、错误 token 类型，返回 `INVALID_REFRESH_TOKEN`

实现建议：

- 不要强依赖复杂的 `instanceof`
- 优先判断 `error` 的 `name`
- 常见判断方式：

```ts
if (error && typeof error === 'object' && 'name' in error) {
  const name = String((error as { name?: string }).name);
  if (name === 'TokenExpiredError') {
    ...
  }
}
```

这一批至少补两条测试：

- `verifyAsync` 抛 `TokenExpiredError` 风格异常 -> `REFRESH_TOKEN_EXPIRED`
- `verifyAsync` 抛 `JsonWebTokenError` / 普通 invalid 异常 -> `INVALID_REFRESH_TOKEN`

保留现有行为：

- `SESSION_REVOKED`
- `TOKEN_REUSE_DETECTED`
- `SESSION_NOT_FOUND`

不要顺手重构整个 refresh 状态机。

### 批次 D：补 auth HTTP 集成测试

目标：让 controller / pipe / guard / wiring 有一层真实 HTTP 回归保护。

推荐新文件：

- `apps/api/test/auth.e2e-spec.ts`

不要直接依赖完整真实基础设施。推荐做法：

- 用 `Test.createTestingModule()`
- 直接注册 `AuthController`
- 使用真实 `AuthGuard`
- mock `OtpService`、`SessionService`、`ConsentService`
- `createNestApplication()` 后用 `supertest`

为什么这样做：

- 这样能测到真正的路由、DTO 校验、guard 挂载和 HTTP 响应
- 但不会被真实 Redis / Postgres / SMS 阻塞

最低必须覆盖这些场景：

1. `POST /auth/login`
   - 成功返回 200 + tokens
   - OTP 业务失败返回 200 + 业务错误体
   - 缺字段或格式错误返回 400

2. `POST /auth/refresh`
   - 成功返回 200 + 新 token
   - 过期返回 200 + `REFRESH_TOKEN_EXPIRED`
   - 无效返回 200 + `INVALID_REFRESH_TOKEN`

3. `GET /auth/consent/status`
   - 不带 token 返回 401
   - token 合法但 session 已撤销返回 401
   - token 合法且 session active 返回 200

建议结构：

- 每个路由一组 `describe`
- 每组里只 mock本路由所需的最少行为
- 文件头注释写清执行命令

## 3. 推荐编辑顺序

为了减少来回返工，按下面顺序改：

1. `auth.controller.ts`
2. `auth-cache.service.ts`
3. `session.service.ts`
4. 对应 unit tests
5. 新增 `apps/api/test/auth.e2e-spec.ts`
6. 如有 contract 变化，再导出 openapi

不要一上来就先写 e2e，再倒推实现。

## 4. 每一批做完后跑什么

### 完成批次 A 后

```bash
corepack pnpm --dir apps/api exec tsc -p tsconfig.json --noEmit
```

### 完成批次 B 后

```bash
corepack pnpm --dir apps/api exec jest src/modules/auth/cache/__tests__/auth-cache.service.spec.ts --runInBand
corepack pnpm --dir apps/api exec jest src/modules/auth/__tests__/otp.service.spec.ts --runInBand
```

### 完成批次 C 后

```bash
corepack pnpm --dir apps/api exec jest src/modules/auth/__tests__/session.service.spec.ts --runInBand
```

### 完成批次 D 后

```bash
corepack pnpm --dir apps/api exec jest test/auth.e2e-spec.ts --runInBand
corepack pnpm --dir apps/api exec jest src/modules/auth --runInBand
corepack pnpm --dir apps/api exec tsc -p tsconfig.json --noEmit
```

## 5. 最容易踩的坑

- 把 `/auth/otp/verify` 的 service 能力一起删了，结果 `/auth/login` 也坏掉
- 修了 `normalizePhone()`，但忘了改测试里的旧 `+86` 预期
- 把 `+86` 直接写进内部 canonical format，导致 cache / repository / createUser 又分叉
- 为了区分 refresh 错误，顺手把现有 `SESSION_REVOKED`、`TOKEN_REUSE_DETECTED` 行为搞乱
- e2e 测试直接 import 完整 `AppModule`，结果被真实基础设施依赖拖住
- 因为想“一步到位”，顺手把 `ValidationPipe` 或 `AuthGuard` 全局化，导致超出本次 change 范围

## 6. 这一步完成的判定标准

满足下面这些，才算 Step 09 做完：

1. `auth` 对外只保留清晰的 OTP 登录主路径
2. 常见大陆手机号格式都能收敛成同一个内部手机号
3. refresh token 过期和无效能返回不同业务错误码
4. auth 有真实 HTTP 集成测试覆盖 login / refresh / protected routes
5. 相关 Jest 和 `tsc --noEmit` 通过

## 7. 如果开发机卡住，优先这样处理

- 先保证 `/auth/login`、手机号规范化、refresh 错误语义三件事正确
- e2e 测试如果一开始太难，先用最小 TestingModule 跑通 `GET /auth/consent/status`
- 不确定该不该删 `/auth/otp/verify` 时，先 grep 仓库调用方；如果没有正式调用，优先删路由而不是继续模糊保留
- 如果发现真实数据或 seed 明显依赖 `+86` 持久化格式，先停下来同步，不要自行做隐式数据迁移
