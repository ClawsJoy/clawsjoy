# ClawsJoy V9 Agent 工作区 — 优化总结

> 2026-07-11 | 四十八次测试 | 109轮崩溃 → 5轮修改

---

## 一、核心成果

| 能力 | 轮数 | 关键优化 |
|------|------|---------|
| 需要修改 | 5 | 任务初始状态驱动 |
| 代码已就绪 | 14 | `status_hint` 打断逐段读 |
| 纯查询 | 6 | `query_index` AST 快速路径 |
| 多文件重构 | 66 | 自修复 + 异步后台执行 |
| 自动测试闭环 | ✅ | 规则4：改→跑→失败→修复→通过 |
| Plan Mode | ✅ | 复杂任务自发规划，多轮自然承载 |

## 二、优化原则

**在 Agent 必然读取的内容里放信号，不在工具箱里加工具。**

- `status_hint`：三行代码节省 8 轮（22→14）
- `query_index`：一次调用替代 6 次逐段读
- `verify`、经验注入、网关注入：需要 Agent 主动选择 → 全部无效

## 三、工具链

| 组件 | 文件 | 说明 |
|------|------|------|
| `status_hint` | `agent_gateway_enhanced.py:1097` | 规则1(测试文件) + 规则2(METHOD_HINTS) |
| `query_index` | `agent_gateway_enhanced.py:1014` | AST 快速路径 + 优先级排序 |
| 异步执行 | `agent_gateway_enhanced.py:898` | max_rounds=100, write_file 对齐 |
| 自动测试闭环 | `agent_system.md:48` | 规则4：最多3次循环 |
| Plan Mode | `agent_system.md:28` | 规则0：自发规划 |
| V8 修复 | `agent_gateway_enhanced.py:284` | task_state + task_engine 同步 |
| 元认知注入 | `agent_gateway_enhanced.py:1687` | optimization_tips 通道 |
| `_get_agent_tools()` | `agent_gateway_enhanced.py:1064` | 消除 tools 定义重复 |

## 四、技术债务（已评估，不处理）

| # | 问题 | 原因 |
|---|------|------|
| 1 | `_execute_sandbox_tool` 重复分支 | 不影响功能 |
| 2 | `query_index` 关键词匹配精度 | 当前够用 |
| 3 | 元认知 evolve 阈值偏高 | Agent 表现好不需要建议 |
| 4 | `verify` 未被调用 | 保留代码 |

## 五、Git 状态

本地 6 个 commit 领先 `origin/fix/remove-hardcoded-secrets`，未推送。
b0a732eb refactor: 提取 _get_agent_tools()
a92ac5b2 fix: 异步引擎 write_file 对齐同步版
963096d1 feat: query_index
460c69f3 feat: 自动测试闭环 + 元认知注入通道
a4141dc1 chore: 清理临时文件
2b492e98 feat: status_hint 规则引擎 + V8 修复 + verify 使用限制
