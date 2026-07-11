# ClawsJoy V8

**AI 劳动力管理平台** — 一人公司老板聘 AI 员工，频道里派活，自动记账。本地运行，开源免费。

## 核心功能

- **聘 AI 员工** — 程序员、设计师、分析师，选模型，设预算，一键聘用

- **频道协作** — 发消息自动路由，AI 员工同频道对话，@指定成员

- **视频逆向工程** — 自动场景检测+逐帧分析+制作手册

- **图片批量管理** — 逐张分析+去重+标签+缩略图+分类整理+导出报告

- **实时记账** — 每次 API 调用自动记录，账单随时查看

- **事件驱动通知** — 任务完成自动 @审查员，审查通过自动通知

- **Discord 集成** — 同频道多 AI 员工协作，Webhook 多身份发言

## 快速开始

```bash

# 1. 安装依赖

pip install -r requirements.txt

# 2. 配置环境变量

cp config/.env.example config/.env

# 编辑 config/.env，填入 YouTube API Key 等

# 3. 启动 Ollama（自动）

python3.10 agent_gateway_enhanced.py

# 4. 打开浏览器

http://localhost:5002/workbench

岗位市场

在 workbench 或 Discord 里聘 AI 员工：

岗位	默认模型	月预算	能力

程序员	Ollama qwen2.5:7b	$5	写代码、修bug、代码审查

设计师	Ollama llava	$15	生成图片、视觉分析

分析师	Ollama qwen2.5:7b	$3	数据分析、竞品监控

支持切换模型：DeepSeek / GLM 5.2 / Claude Code。

技术架构

Gateway (Flask 5002)
  ↓
Cortex (意图路由: 规则→fastText→向量语义→正则→兜底)
  ↓
Agent (23个内置 + 适配器扩展)
  ↓
Ollama 双实例 (GPU: qwen2.5:7b / CPU: llava)

V8 劳动力管理层：core/lib/v8/（非侵入式，不碰 v6/v7 代码）

文档

用户指南

开发者文档

系统要求

Python 3.10+

Ollama

6GB+ 显存（推荐 RTX 2060+）

Linux / WSL2

开源协议

MIT License


作者

ClawsJoy — 知乎主页:https://www.zhihu.com/people/john-18-20
