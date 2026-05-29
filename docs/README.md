# ClawsJoy 4.0 - 智能体操作系统

[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/clawsjoy/clawsjoy)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13+-yellow.svg)](https://python.org)

## 简介

ClawsJoy 4.0 是一个企业级智能体操作系统，支持多 Agent 协作、用户数字分身、隐私保护和安全通信。

## 核心特性

- 🤖 **10+ 智能 Agent**：决策、聊天、执行、采集、安全、管家、分析等
- 🎯 **20+ 原子技能**：图像生成、任务调度、视频处理等
- 🔒 **隐私保护**：用户数据隔离、端到端加密、本地脱敏
- ⚙️ **配置驱动**：所有行为可配置，无需修改代码
- 🧠 **记忆系统**：四层渐进式记忆架构（L0-L4）
- 🔐 **安全通信**：HTTPS + JWT 认证
- 📊 **监控体系**：看门狗、旁路监控、健康检查
- 🐳 **容器化**：Docker 一键部署

## 快速开始

### 环境要求

- Python 3.13+
- 8GB+ RAM
- 10GB+ 磁盘空间

### 安装

```bash
# 克隆仓库
git clone https://github.com/clawsjoy/clawsjoy.git
cd clawsjoy

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env

# 启动服务
./start_all.sh
访问服务
Web 界面: https://localhost:5446

健康检查: https://localhost:5446/api/health

服务状态: https://localhost:5446/api/services

测试账号
用户名: user1

密码: admin123

架构设计
┌─────────────────────────────────────────────────────────────┐
│                    用户层                                    │
├─────────────────────────────────────────────────────────────┤
│                    安全层 (HTTPS + JWT)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │决策Agent│ │聊天Agent│ │执行Agent│ │采集Agent│           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │安全Agent│ │管家Agent│ │分析Agent│ │记忆Agent│           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────┤
│                    技能层 (20+ 原子技能)                     │
├─────────────────────────────────────────────────────────────┤
│                    记忆层 (L0-L4 渐进式)                     │
└─────────────────────────────────────────────────────────────┘
项目结构
clawsjoy/
├── core/                    # 核心代码
│   ├── lib/                 # 核心库
│   ├── intelligence/        # 智能模块
│   └── agents/              # Agent 系统
├── skills/                  # 原子技能
├── config/                  # 配置文件
├── web/                     # Web 界面
├── docs/                    # 文档
└── scripts/                 # 工具脚本
文档
用户指南

管理员指南

架构师指南

Agent 手册

API 参考

贡献
欢迎提交 Issue 和 Pull Request！

许可证
MIT License

联系方式
项目主页: https://github.com/clawsjoy/clawsjoy

问题反馈: https://github.com/clawsjoy/clawsjoy/issues

Made with ❤️ by ClawsJoy Team
