# 🦞 ClawsJoy - 开源多租户 AI 调度平台

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/ClawsJoy/ClawsJoy)](https://github.com/ClawsJoy/ClawsJoy/releases)
[![Docker pulls](https://img.shields.io/docker/pulls/18123638984/clawsjoy)](https://hub.docker.com/r/18123638984/clawsjoy)
[![GitHub stars](https://img.shields.io/github/stars/ClawsJoy/ClawsJoy)](https://github.com/ClawsJoy/ClawsJoy/stargazers)

**ClawsJoy** 是一个开源的多租户 AI 调度平台，让每个租户拥有专属的、可插拔的 AI 执行引擎。

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🧠 **AI 调度引擎** | 智能任务编排，支持 Workflow 并行/条件/暂停恢复 |
| 🧩 **Skills 体系** | 可扩展的技能库，热加载，支持自定义 |
| 👥 **多租户隔离** | 数据、配置、资源完全隔离 |
| 🎤 **语音交互** | 自然语言对话，智能响应 |
| 🎬 **宣传片制作** | 自动采集图片、合成视频、TTS 配音 |
| 📁 **资料库管理** | 上传、预览、检索 |
| 💰 **计费系统** | 按量计费，余额管理 |
| 📊 **可视化监控** | Workflow 执行状态实时展示 |

## 🚀 快速开始

### 一键安装（推荐）
```bash
curl -fsSL https://raw.githubusercontent.com/ClawsJoy/ClawsJoy/main/install.sh | bash
Docker 运行
docker run -d -p 8082:8082 -p 8088:8088 -p 8090:8090 -p 8092:8092 18123638984/clawsjoy:latest
🌐 访问地址
页面	地址
租户登录	http://localhost:8082/tenant/
Joy Mate	http://localhost:8082/joymate/?tenant=1
Workflow 监控	http://localhost:8082/workflow/
API 文档	http://localhost:8094/
默认账号: admin / admin123

📊 服务端口
服务	端口
auth	8092
tenant	8088
billing	8090
promo	8086
coffee	8085
router	8089
queue	8091
task	8084
joymate	8080
web	8082
🧩 Skills 体系
Skill	功能
auth	用户认证
tenant	租户管理
billing	计费系统
promo	宣传片制作
coffee	咖啡订购
spider	图片采集
router	消息路由
queue	任务队列
task	任务调度
memory	记忆检索
executor	执行引擎适配
🎬 功能演示
宣传片制作
输入 制作上海科技宣传片，系统自动：

采集图片

生成文案

TTS 配音

合成视频

语音交互
点击麦克风按钮，直接语音输入

资料库管理
点击「我的资料库」，上传、预览、检索文件

🏗️ 技术架构
text
用户输入 → Joy Mate 前端 (8082) → task_api 调度器 (8084)
    ↓
租户隔离 / 计费扣款 / 任务记录
    ↓
执行层 (promo_api/coffee_api/...)
    ↓
返回结果
📖 文档
安装指南

API 文档

开发指南

🤝 贡献
欢迎贡献代码、报告问题、提出建议。

📄 许可证
Apache 2.0 License

📧 联系
GitHub: https://github.com/ClawsJoy/ClawsJoy

Issues: https://github.com/ClawsJoy/ClawsJoy/issues

Made with ❤️ by ClawsJoy Team
