# ClawsJoy 3.0

原子技能 + 大脑调度 + 记忆驱动的智能体系统

## 核心特性

- 🧠 **大脑调度**：LLM 自主决策调用哪些技能
- 💾 **记忆系统**：成功/失败经验存储，下次复用
- 🎯 **自校准**：时长与字数自动换算调整
- 🔧 **质量门**：逐环节独立检验
- 🛡️ **自愈框架**：自动识别并修复常见问题
- 🎬 **漫剧制作**：一键生成视频

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

# 启动网关
python3 agent_gateway_web.py
核心模块
模块	说明
skills/	原子技能库 (120+)
agent_core/	大脑核心
lib/memory_simple.py	记忆系统
skills/do_anything.py	LLM 调度器
skills/manju_maker.py	漫剧制作
skills/calibrated_executor.py	自校准执行器
使用示例
from skills.calibrated_executor import skill

# 生成视频
result = skill.execute({
    'topic': '香港高才通续签率',
    'target_duration': 60
})
print(result['video'])
许可证
MIT License

注意事项
敏感配置不提交，请自行配置 .env

OAuth token 本地生成，不共享

首次使用需配置 YouTube API 授权

贡献
欢迎提交 Issue 和 Pull Request
