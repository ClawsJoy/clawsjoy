# ClawsJoy V9

**AI 劳动力管理平台 + Agent 工作区** — 一人公司老板聘 AI 员工，频道里派活。Agent 工作区提供代码修改、测试验证、异步执行、代码索引等开发能力。本地运行，开源免费。

## 核心功能

### V8 团队频道
- **聘 AI 员工** — 程序员、设计师、分析师，选模型，设预算
- **频道协作** — 发消息自动路由，AI 员工同频道对话
- **视频/图片处理** — 逆向工程、逐帧分析、去重标签
- **实时记账** — API 调用自动记录
- **Discord 集成** — Webhook 多身份发言

### V9 Agent 工作区
- **代码修改** — 单文件 5 轮，多文件自修复
- **自动测试闭环** — 改→跑→失败→修复→通过，最多 3 次循环
- **代码索引查询** — `query_index` 一次调用替代逐段读文件
- **异步后台执行** — 复杂任务后台跑，前端轮询进度
- **智能规划** — 复杂任务自发列出执行计划，多轮对话确认后执行

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp config/.env.example config/.env
# 编辑 config/.env，填入 DeepSeek API Key、Discord Token 等

# 3. 启动
python3 agent_gateway_enhanced.py

# 4. 打开浏览器
# 团队频道: http://localhost:5002/workbench
# Agent 工作区: http://localhost:5002/

##技术架构

Gateway (Flask 5002)
  ↓
Cortex (意图路由: 规则→fastText→向量语义→正则→兜底)
  ↓
Agent (24个内置 + 适配器扩展)
  ↓
DeepSeek v4 Flash / GLM 5.2 / Ollama

##优化体系

能力	效果	机制
status_hint	22→14 轮	read_file content 顶部植入提示
query_index	替代逐段读	AST 快速路径 + 关键词匹配
自动测试闭环	完整触发	规则4：最多 3 次循环
Plan Mode	自发规划	复杂任务自然触发
异步执行	后台运行	max_rounds=100

##文档

CLOSING_SUMMARY.md — 四十八次测试优化总结

CHANGELOG.md — 版本变更记录

docs/ — 用户指南 + 开发者文档

##系统要求

Python 3.10+

6GB+ 显存（推荐 RTX 2060+）

Linux / WSL2

##开源协议

MIT License
