# ClawsJoy / JoyMate

> 轻量化 AI 管家系统 | 租户隔离 | 关键词驱动 | 工作流编排

## 🎯 核心特性

- 🤖 **Agent 管家** - 每个租户专属管家，自动干活
- 🔒 **租户隔离** - 数据完全私有，不上传云端
- 🎬 **视频生成** - 自动采集图片 + TTS 配音 + 合成视频
- 📝 **关键词驱动** - 自动采集和扩展关键词
- 🔧 **工作流编排** - 积木式组合任务
- 🐳 **一键部署** - Docker Compose 快速启动

## 🚀 快速开始

### 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/ClawsJoy/ClawsJoy/main/install.sh | bash
Docker 部署
git clone https://github.com/ClawsJoy/ClawsJoy.git
cd ClawsJoy
docker-compose up -d
访问服务
Web 界面: http://localhost:18082/joymate/index.html?tenant=1

Agent API: http://localhost:18103/api/agent/chat
📁 项目结构
clawsjoy/
├── bin/           # 核心服务（开源）
├── skills/        # Skill 积木（开源）
├── workflows/     # 工作流定义（开源）
├── web/           # 前端界面（开源）
├── tenants/       # 租户数据（私有，不推送）
└── data/          # 运行时数据（私有）
🔧 创建新租户
./bin/init_tenant.sh tenant_2
📊 服务端口
服务	端口
Web 前端	 18082
Chat API	         18101
Promo API	 8108
Agent API	18103
TTS  	        9000
📄 License
Apache 2.0
🙏 致谢
Ollama - 本地大模型

Unsplash - 图片采集

FFmpeg - 视频合成
