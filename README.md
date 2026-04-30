# 🦞 ClawsJoy - 多租户 AI 调度平台

<div align="center">

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Docker Pulls](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com/r/clawsjoy/clawsjoy)

**让 AI 像一支专业团队一样为你工作**

</div>

## 📖 简介

ClawsJoy 是一个开源的多租户 AI 调度平台，让每个租户拥有专属的、可插拔的 AI 执行引擎。

### 🎯 为什么选择 ClawsJoy？

- **🚀 开箱即用**：一键安装，1-2秒生成宣传片
- **🔐 数据安全**：私有化部署，租户数据完全隔离
- **🔌 可插拔**：支持 OpenClaw、Claude Code 等多种 AI 引擎
- **💰 内置计费**：按量计费，余额管理
- **📊 可视化监控**：Workflow 执行状态实时展示

## ✨ 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| 🎬 **宣传片生成** | 自动采集图片、合成视频 | ✅ 稳定 |
| ☕ **咖啡订购** | 集成咖啡订购功能 | ✅ 稳定 |
| 👥 **多租户隔离** | 数据、配置、资源完全隔离 | ✅ 稳定 |
| 💰 **计费系统** | 按量计费，余额管理 | ✅ 稳定 |
| 🔐 **企业级认证** | 邮箱验证、密码重置、JWT | ✅ 稳定 |
| 🧠 **Skills 体系** | 可扩展的技能库，热加载 | ✅ 稳定 |
| 📊 **Workflow 监控** | 实时查看执行状态 | ✅ 稳定 |

## 🏗️ 系统架构
┌─────────────────────────────────────────────────────────────────┐
│ 用户 (租户) │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Joy Mate (前端) │
│ http://localhost:8082 │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ task_api (调度器) │
│ http://localhost:8084 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ 租户隔离 │ │ 计费扣款 │ │ 任务记录 │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ promo_api (执行层) │
│ http://localhost:8086 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ 采集图片 │ │ 合成视频 │ │ 返回成品 │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘

## 🚀 快速开始

### 方式一：一键安装（推荐）

```bash
git clone https://github.com/ClawsJoy/clawsjoy.git
cd clawsjoy/installers
./install.sh

###方式二：Docker 运行

```bash
docker run -d \
  --name clawsjoy \
  -p 8082:8082 -p 8088:8088 -p 8090:8090 -p 8092:8092 \
  clawsjoy/clawsjoy:latest

###方式三：源码运行

```bash
git clone https://github.com/ClawsJoy/clawsjoy.git
cd clawsjoy
pip install -r bin/requirements.txt
pm2 start ecosystem.config.js

🌐 访问地址
页面	地址	说明
租户登录	http://localhost:8082/tenant/	登录入口
Joy Mate	http://localhost:8082/joymate/?tenant=1	AI 助手
Workflow 监控	http://localhost:8082/workflow/	状态监控
API 文档	http://localhost:8094/	接口文档
默认账号: admin / admin123

🧪 快速测试

```bash
# 测试租户 API
curl http://localhost:8088/api/tenants

# 生成宣传片
curl -X POST http://localhost:8084/api/task/promo \
  -H "Content-Type: application/json" \
  -d '{"city":"香港","tenant_id":"1"}'

# 查询余额
curl "http://localhost:8090/api/billing/balance?tenant_id=1"

# 咖啡店列表
curl http://localhost:8085/api/coffee/shops

🔧 配置 OpenClaw 集成
ClawsJoy Skills 可以通过软链接被 OpenClaw 调用：

bash
cd installers
./install.sh

📖 文档
文档	说明
安装指南	详细安装步骤
API 文档	接口说明
运维手册	运维指南
OpenClaw 集成	集成说明

🤝 贡献
欢迎贡献代码、报告问题、提出建议！

Fork 仓库

创建功能分支: git checkout -b feature/xxx

提交代码: git commit -m "feat: xxx"

推送: git push origin feature/xxx

创建 Pull Request

📄 许可证
Apache 2.0 License

📧 联系
GitHub: https://github.com/ClawsJoy/clawsjoy

Issues: https://github.com/ClawsJoy/clawsjoy/issues

讨论: https://github.com/ClawsJoy/clawsjoy/discussions

⭐ 如果这个项目对你有帮助，请给个 Star！

让 AI 像一支专业团队一样为你工作！ 🦞
