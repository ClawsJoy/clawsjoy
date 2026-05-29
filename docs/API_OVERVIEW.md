# ClawsJoy API Overview

本文档汇总 `bin/*api.py` 当前对外接口，方便联调、排错和后续重构。

## Service Ports

- `auth_api.py` -> `8092`
- `tenant_api.py` -> `8088`
- `billing_api.py` -> `8090`
- `task_api.py` -> `8084`
- `joymate_api.py` -> `8080`
- `coffee_api.py` -> `8085`
- `promo_api.py` -> `8086`

## Auth API (`/api/auth`, port 8092)

- `GET /api/auth/health`
  - 用途: 健康检查
  - 返回: `{"status":"ok"}`

- `POST /api/auth/login`
  - 请求体: `username`, `password`
  - 返回成功: `token` + `user{name, tenant_id, role}`
  - 返回失败: `401` + 错误信息

- `POST /api/auth/register`
  - 请求体: `username`, `password`, 可选 `tenant_id`
  - 行为: 创建普通用户（`role=user`）

## Tenant API (`/api/tenants`, port 8088)

- `GET /api/tenants`
  - 用途: 列出租户（从 `tenants/tenant_*` 推导）

- `GET /api/tenants/<tenant_id>`
  - 用途: 获取租户配置
  - 说明: 若缺少 `config.json`，返回默认配置

- `GET /api/tenants/stats`
  - 用途: 租户统计（按租户目录下 `*.json` 文件数统计任务量）

- `POST /api/tenants`
  - 请求体: 可选 `id`, 可选 `name`
  - 行为: 创建租户目录并写入 `config.json`

- `POST /api/tenants/config`
  - 请求体: `tenant_id`, `config`
  - 行为: 顶层字段浅覆盖更新配置

- `DELETE /api/tenants/<tenant_id>`
  - 行为: 删除对应租户目录

## Billing API (`/api/billing`, port 8090)

- `GET /api/billing/balance?tenant_id=<id>`
  - 用途: 查询租户余额

- `GET /api/billing/usage?tenant_id=<id>&days=<n>`
  - 用途: 查询租户在 `n` 天内的任务用量统计

- `GET /api/billing/admin/tenants?days=<n>`
  - 用途: 管理员查看所有租户用量汇总

- `GET /api/billing/plans`
  - 用途: 获取套餐列表

- `POST /api/billing/record`
  - 请求体: `tenant_id`, `task_type`, `quantity`
  - 行为: 记录计费并扣减余额

- `POST /api/billing/recharge`
  - 请求体: `tenant_id`, `amount`
  - 行为: 余额充值

## Task API (`/api/task`, port 8084)

- `POST /api/task/submit`
  - 请求体: `tenant_id`, `task_type`, `params`
  - 行为: 写入队列任务文件到 `/tmp/tenants/queue`
  - 返回: `task_id`

- `GET /api/task/status`
  - 用途: 轻量状态检查
  - 可选请求头: `X-Tenant-Id`

## JoyMate API (port 8080)

- `GET /api/memory/retrieve?tenant_id=<id>&query=<text>`
  - 用途: 记忆检索（关键词匹配 `LEARNINGS.md`）

- `GET /api/tasks?tenant_id=<id>`
  - 用途: 读取 `/tmp/tenants/queue` 任务列表

- `GET /api/skills`
  - 用途: 列出 `skills/auto_generated` 下技能文件

- `POST /api/task/submit`
  - 用途: 提交任务文件到 `/tmp/tenants/queue`

- `POST /api/memory/record`
  - 请求体: `tenant_id`, `agent`, `title`, `date`, `content`
  - 行为: 追加写入 `LEARNINGS.md`

## Coffee API (`/api/coffee`, port 8085)

- `GET /api/coffee/shops?keyword=<kw>`
  - 用途: 检索咖啡店（店名/菜单关键字）

- `GET /api/coffee/menu?shop_id=<id>`
  - 用途: 查询店铺菜单

- `GET /api/coffee/orders?user_id=<id>`
  - 用途: 查询用户订单历史（最近 10 条）

- `POST /api/coffee/order`
  - 请求体: `user_id`, `shop_id`, `shop_name`, `item`, `price`
  - 行为: 创建订单并写入 `data/orders.json`

## Promo API (`/api/promo`, port 8086)

- `GET /api/promo/make?city=<城市>&style=<风格>`
- `POST /api/promo/make`
  - 请求体: `city`, `style`
  - 行为: 调用采图脚本 + 视频生成脚本
  - 返回: 成功时附带 `video_url`

## Common Behavior

- 多数 API 返回 `application/json`
- 多数 API 允许跨域（`Access-Control-Allow-Origin: *`）
- 大多数服务关闭了默认访问日志（或仅打印简要日志）

## Logging Baseline

- 统一日志目录分层:
  - `logs/app/`：各 API 服务日志
  - `logs/runner/`：任务执行器日志
  - `logs/audit/`：审计日志
  - `logs/system/`：启动与系统脚本日志
- Shell 日志格式统一为:
  - `[ISO8601时间] [service] [level] message`
- 已提供 logrotate 配置与安装脚本:
  - `ops/logrotate/clawsjoy.conf`
  - `bin/install_logrotate.sh`

## Known Inconsistencies

- 当前已引入统一配置层:
  - Python: `bin/settings.py`
  - Shell: `bin/settings.sh`
- 路径与端口支持环境变量覆盖:
  - 根路径: `CLAWSJOY_ROOT`
  - 队列路径: `CLAWSJOY_TASK_QUEUE_DIR`
  - 端口: `CLAWSJOY_PORT_*`
