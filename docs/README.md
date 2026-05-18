# ClawsJoy 3.0
🧠 ClawsJoy 智能系统

本地化 · 可扩展 · 自进化的智能任务自动化平台
https://img.shields.io/badge/license-MIT-blue.svg
https://img.shields.io/badge/python-3.11+-green.svg
https://img.shields.io/badge/status-stable-brightgreen.svg

## 核心特性

- 🧠 大脑调度 - LLM 驱动的任务规划与执行
- 💾 记忆系统 - 经验积累 + 向量语义检索
- 🎯 原子技能 - 63 个可组合的原子技能
- 🔧 Web 仪表板 - 可视化监控和管理
- 🛡️ 完整 API - Swagger 文档 + Prometheus 监控
- 🎬 多智能体 - 5 个专业化 Agent 协作

## 快速开始

### 环境要求

- Python 3.10+
- Ollama (qwen2.5:7b)
- ffmpeg
- edge-tts

### 安装

```bash
# 克隆仓库
git clone https://github.com/ClawsJoy/clawsjoy.git
cd clawsjoy

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的配置
配置 .env
# YouTube API
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_CHANNEL_ID=your_channel_id

# Unsplash API (可选)
UNSPLASH_ACCESS_KEY=your_unsplash_key
启动
# 启动 Ollama
ollama serve

# # 启动服务
./start_all.sh

# # 访问 Web Dashboard
open http://localhost:5011
#📚 文档
部署指南

开发指南

API 文档

#架构设计
📡 服务端口
服务	端口
API Gateway	5002
Web Dashboard	5011
注册中心	5022
定时任务	5023
技能市场	5024

#🤝 贡献
欢迎提交 Issue 和 Pull Request！

📄 许可证
MIT License

注意事项
敏感配置不提交，请自行配置 .env

OAuth token 本地生成，不共享

首次使用需配置 YouTube API 授权

