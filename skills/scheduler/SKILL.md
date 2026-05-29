---
name: scheduler
version: 1.0.0
description: '任务调度技能，支持定时任务和周期性任务 Use when: 需要定时执行任务、设置周期性提醒、管理 cron 任务 NOT for: 实时任务执行、一次性立即执行

  '
author: ClawsJoy
security_grade: 🟡 B
use_when: 定时任务, 调度任务, 周期性执行
not_for: 实时执行
---



# Task Scheduler

## When to Run
- 用户说"定时执行"、"每天 X 点运行"
- 设置周期性任务
- 管理现有定时任务

## Workflow
1. 解析调度规则
2. 验证 cron 表达式
3. 添加到调度队列
4. 返回任务 ID

## Output Format
```json
{
  "success": true,
  "task_id": "scheduled_task_xxx",
  "next_run": "2026-05-18 08:00:00"
}
Changelog
v1.0.0 (2026-05-17)
初始版本
