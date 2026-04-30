# ClawsJoy v0.2 Engineering Baseline

发布日期：2026-04-28
发布类型：工程化基线升级（有条件通过）

## 本次完成

- API 注释标准化：`bin/*api.py` 关键接口与核心逻辑注释补齐。
- 接口基线文档：新增并维护 `API_OVERVIEW.md`。
- 统一配置层：
  - Python：`bin/settings.py`
  - Shell：`bin/settings.sh`
  - 模板：`bin/env.example`
- 路径/端口配置化：核心 API 与 `task_runner.sh` 已从硬编码迁移到配置驱动。
- 任务执行器增强：错误处理、失败隔离、审计日志、函数化、`trap` 回滚。
- 最小 CI：新增 `.github/workflows/ci.yml`（Python/Shell 语法检查）。
- 日志工程化：
  - 分层日志目录：`logs/app`、`logs/runner`、`logs/audit`、`logs/system`
  - 统一 shell 日志格式：`[time] [service] [level] message`
  - logrotate 配置：`ops/logrotate/clawsjoy.conf`
  - 安装脚本：`bin/install_logrotate.sh`
- 运维三件套：
  - `bin/start_clawsjoy.sh`
  - `bin/stop_clawsjoy.sh`
  - `bin/status_clawsjoy.sh`

## 验收结论

当前状态：**有条件通过**

### 通过项

- API 注释标准化
- `API_OVERVIEW.md` 同步
- 统一配置层
- 路径配置化
- `task_runner.sh` 改造
- 最小 CI
- 运维三件套

### 条件项（待整改）

- Python API 日志格式需与 shell 侧进一步统一。
- 启停链路需完成一次实机端到端联调验证。
- logrotate 参数需结合生产策略确认（当前 `daily/rotate14/size20M`）。
- `status` 建议增强端口探活（当前以 pid 检查为主）。
- `trap` 回滚策略是否扩展信号与回滚审计待确认。

## 已知限制

- 当前执行环境缺少可用 `bash` 运行时（`/bin/bash` 不可用），导致会话内无法直接完成 `start/status/stop` 脚本实测。

## 下一步计划

1. 补齐 Python API 统一日志输出适配。
2. 在具备 bash 的目标环境执行端到端联调并留存结果。
3. 确认并固化 logrotate 生产参数。
4. 增强 `status` 端口探活并补充失败原因分类。
