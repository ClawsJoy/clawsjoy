# ClawsJoy v5.4.0 - 智慧化智能助手系统

## 简介
ClawsJoy 是一个基于 LLM 的**智慧化智能助手系统**，支持多 Agent 协作、联邦学习、主动服务、科学计算和多语言翻译。

## 版本特性

### v5.4.0 - 智慧化升级 (当前版本)
- 🧠 **8个智慧Agent**: Chat/Code/Analysis/Butler/Translate/Calculator/Orchestrator/Decision
- 🤝 **联邦学习**: Agent间知识共享与协作
- 💡 **主动服务**: 基于用户画像的主动建议
- ⚡ **性能优化**: LRU缓存、批处理、智能模型选择
- 📊 **科学计算器**: 支持 sqrt/sin/cos/log/factorial 等
- 🌐 **多语言翻译**: 中、英、日、韩、法、德、西、俄等
- 🎯 **任务编排**: 复杂任务自动分解与调度
- 📋 **JSON标准库**: 2.5层混合设计，LLM友好

### v5.3.0 - 基础版本
- 多轮对话记忆
- 持久化存储
- 意图识别
- 代码生成

## 系统架构
┌─────────────────────────────────────────────────────────────┐
│ ClawsJoy 智慧化系统 │
├─────────────────────────────────────────────────────────────┤
│ 🤖 Agent 层 │
│ ├── ChatAgent - 对话、记忆、情感、主动建议 │
│ ├── CodeAgent - 代码生成、解释、调试、优化 │
│ ├── AnalysisAgent - 数据分析、框架提供 │
│ ├── ButlerAgent - 私人管家、待办管理 │
│ ├── TranslateAgent - 多语言翻译 │
│ ├── CalculatorAgent- 科学计算 │
│ ├── Orchestrator - 任务编排、分解、调度 │
│ └── DecisionAgent - 路由决策、置信度校准 │
├─────────────────────────────────────────────────────────────┤
│ 🔧 增强模块 │
│ ├── 联邦学习 - Agent间知识共享 │
│ ├── 主动服务 - 基于用户画像的主动建议 │
│ └── 性能优化 - 缓存、批处理、模型选择 │
└─────────────────────────────────────────────────────────────┘

## 快速开始

### 环境要求
- Python 3.10+
- Ollama (用于本地 LLM)
- 推荐模型: qwen2.5:3b/7b, codellama:7b, phi3:mini

### 安装

```bash
# 克隆仓库
git clone <repository>
cd clawsjoy_v5

# 安装依赖
pip install -r requirements.txt

# 拉取推荐模型
ollama pull qwen2.5:3b
ollama pull qwen2.5:7b
ollama pull codellama:7b
ollama pull phi3:mini

# 启动服务
./start_clawsjoy.sh
#API 使用
#智慧对话接口
# 自然语言输入
curl -X POST http://localhost:5002/api/v5/wisdom/chat \\
  -H "Content-Type: application/json" \\
  -d '{"user_id":"test", "agent":"chat_agent", "message":"你好"}'

# 标准化 JSON 输入
curl -X POST http://localhost:5002/api/v5/wisdom/chat \\
  -H "Content-Type: application/json" \\
  -d '{"user_id":"test", "action":"chat", "target":"text", "raw_input":"你好"}'

# 指定 Agent
curl -X POST http://localhost:5002/api/v5/wisdom/chat \\
  -H "Content-Type: application/json" \\
  -d '{"user_id":"test", "agent":"code_agent", "message":"写一个排序函数"}'
#Agent 示例
Agent	请求示例	说明
chat_agent	{"message":"我叫张三"}	名字记忆
chat_agent	{"message":"我喜欢颜色是蓝色"}	偏好记忆
code_agent	{"message":"写一个快速排序"}	代码生成
analysis_agent	{"message":"分析销售数据"}	数据分析
translate_agent	{"message":"中译英：你好"}	多语言翻译
calculator_agent	{"message":"sqrt(16) + 3^2"}	科学计算
butler_agent	{"message":"添加待办 买牛奶"}	待办管理
orchestrator	{"message":"分析数据然后生成图表"}	任务编排
#决策统计接口
# 查看决策学习统计
curl -X GET "http://localhost:5002/api/v5/wisdom/decision/stats?user_id=test"

# 提供决策反馈
curl -X POST http://localhost:5002/api/v5/wisdom/decision/feedback \\
  -H "Content-Type: application/json" \\
  -d '{"user_id":"test", "task_id":0, "was_correct":true}'

# 查看决策历史
curl -X GET "http://localhost:5002/api/v5/wisdom/decision/history?user_id=test&limit=10"
#功能特性
✅ 已实现
8个智慧Agent: 覆盖对话、代码、分析、管家、翻译、计算、编排、决策

联邦学习: Agent间知识共享，持续学习

主动服务: 基于用户画像的智能建议

元认知: 置信度量化、经验学习

任务分解: 复杂任务自动拆解

科学计算: 17种数学函数支持

多语言翻译: 10+ 语言互译

JSON标准化: 2.5层混合设计

多模型支持: qwen2.5/codellama/phi3

性能优化: LRU缓存、批处理

🔄 开发中
更多 Agent 扩展

强化学习优化

可视化监控面板

配置说明
配置文件位于 config/ 目录:

文件	说明
intents.yaml	意图定义
intent_agent_map.yaml	Agent 映射
system_unified.yaml	系统配置
routes.yaml	路由配置
模型配置
编辑 core/agents/business/business_agent.py 中的模型选择策略：
def _select_model(self, user_input: str) -> str:
    # 科学计算任务
    if "sqrt" in user_input or "sin" in user_input:
        return "qwen2.5:7b"
    # 代码任务
    if "代码" in user_input:
        return "codellama:7b"
    # 默认
    return "qwen2.5:3b"
#目录结构
clawsjoy_v5/
├── agents/              # Agent 实现
│   ├── chat_agent/      # 对话 Agent
│   ├── code_agent/      # 代码 Agent
│   ├── analysis_agent/  # 分析 Agent
│   ├── butler_agent/    # 管家 Agent
│   ├── translate_agent/ # 翻译 Agent
│   ├── calculator_agent/# 计算 Agent
│   ├── orchestrator/    # 编排 Agent
│   └── decision_agent/  # 决策 Agent
├── core/                # 核心库
│   ├── agents/          # Agent 基类
│   ├── lib/             # 工具库
│   │   ├── federated/   # 联邦学习
│   │   ├── proactive/   # 主动服务
│   │   └── performance/ # 性能优化
│   └── ...
├── config/              # 配置文件
├── data/                # 数据存储
└── tests/               # 测试用例
#许可证
MIT

贡献
欢迎提交 Issue 和 Pull Request。

联系方式
项目主页: #

文档: #
