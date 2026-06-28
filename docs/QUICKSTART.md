# ClawsJoy 快速开始

## 环境要求
- Python 3.10+
- Ollama (qwen2.5:7b, llava, nomic-embed-text)
- 8GB+ RAM, NVIDIA GPU (可选)

## 安装

```bash
cd ~/clawsjoy_v5
./install.sh

##启动
# 启动 Ollama
ollama serve &
OLLAMA_HOST=127.0.0.1:11435 OLLAMA_NUM_GPU=0 ollama serve &

# 启动 ClawsJoy
python agent_gateway_enhanced.py

##第一条对话
curl -X POST http://127.0.0.1:5002/v5/execute \
  -H "Content-Type: application/json" \
  -d '{"user_input": "你好", "user_id": "demo"}'
##可用能力
类型	数量	示例
Agent	23	聊天、计算、翻译、写作、记忆
Skill	27	天气、时间、版本、网络、SVG、字幕
##架构
用户输入 → cortex (fastText意图识别 → YAML匹配 → 执行分发) → Agent/Skill → 回复
##更多
API 文档
GitHub
