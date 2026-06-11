# ClawsJoy v5.1 - 智能助手系统

## 简介
ClawsJoy 是一个基于 LLM 的智能助手系统，支持多轮对话、持久化记忆、意图识别和代码生成等功能。

## 快速开始

### 环境要求
- Python 3.10+
- Ollama (用于本地 LLM)
- Redis (可选，用于缓存)

### 安装
```bash
# 克隆仓库
git clone <repository>
cd clawsjoy_v5

# 安装依赖
pip install -r requirements.txt

# 启动服务
./start_clawsjoy.sh
#API 使用
# 对话接口
curl -X POST http://localhost:5002/api/v5/enhanced/chat \\
  -H "Authorization: Bearer <token>" \\
  -d '{"message":"你好","user_id":"test"}'
#功能特性
#✅ 多轮对话记忆

#✅ 持久化存储 (JSON)

#✅ 意图识别 (10+ 意图)

#✅ 代码生成

#✅ 智能缓存

#✅ 流式响应

#配置说明
#配置文件位于 config/ 目录:

#intents.yaml - 意图定义

#intent_agent_map.yaml - Agent 映射

#许可证
#MIT
