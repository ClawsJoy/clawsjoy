<div align="center">

# 🧠 ClawsJoy 智能系统

**本地化 · 可扩展 · 自进化的智能任务自动化平台**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)]()

</div>

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🧠 **大脑调度** | LLM 驱动的智能任务规划与执行 |
| 🔧 **原子技能** | 可自由组合的技能体系，易于扩展 |
| 💾 **记忆系统** | 经验积累 + 向量语义检索 |
| 🤖 **多智能体** | 专业化 Agent 协作完成复杂任务 |
| 📊 **Web 仪表板** | 可视化监控和管理 |
| 🐳 **Docker 部署** | 一键启动，环境隔离 |

---

## 🚀 快速开始

### Docker 部署（推荐）

```bash
# 启动服务
./start.sh docker

# 访问 Web Dashboard
open http://localhost:5011
本地部署
# 安装依赖
pip install -r requirements.txt

# 启动服务
./start.sh local

# 停止服务
./start.sh stop

# 查看状态
./start.sh status

📡 API 端点

端点	                         方法	    说明
/api/health	                   GET	  健康检查
/api/skills	                   GET	  技能列表
/api/skills/<name>	           GET	  技能详情
/api/skills/execute	           POST	  执行技能
/api/agent/v3/do_anything	     POST	  大脑调度
/api/services	                 GET	  服务列表
/api/config	                   GET	  配置信息

🎯 使用示例

数学计算
curl -X POST http://localhost:5002/api/agent/v3/do_anything \
  -H "Content-Type: application/json" \
  -d '{"goal": "100 加 200"}'

# 返回: {"result": 300}
视频制作
curl -X POST http://localhost:5002/api/agent/v3/do_anything \
  -H "Content-Type: application/json" \
  -d '{"goal": "制作一个香港高才通介绍视频"}'

# 返回: 视频文件路径和时长
图片抠图
curl -X POST http://localhost:5002/api/agent/v3/do_anything \
  -H "Content-Type: application/json" \
  -d '{"goal": "抠图 image.jpg"}'

# 返回: 透明背景图片路径
JSON 解析
curl -X POST http://localhost:5002/api/skills/execute \
  -H "Content-Type: application/json" \
  -d '{"skill": "json_parser", "params": {"operation": "parse", "data": "{\"name\":\"ClawsJoy\"}"}}'

  📁 项目结构
  clawsjoy/
├── agent_gateway_web.py   # API 网关
├── file_service_complete.py # 文件服务
├── multi_agent_service_v2.py # 多智能体
├── web_server.py          # Web Dashboard
├── skills/                # 原子技能目录
├── agents/                # 智能体目录
│   ├── core/              # 核心 Agent
│   ├── custom/            # 自定义 Agent
│   └── tools/             # 工具 Agent
├── lib/                   # 核心库
│   ├── config.py          # 配置中心
│   ├── memory_vector.py   # 向量记忆
│   ├── llm_manager.py     # 多模型管理
│   └── smart_adapter.py   # 智能适配器
├── config/                # 配置文件
│   ├── config.yaml        # 主配置
│   └── skills/            # 技能声明
├── data/                  # 数据存储
├── logs/                  # 日志目录
└── output/                # 输出目录

🔧 配置说明
主配置文件 config/config.yaml：
services:
  gateway:
    port: 5002
  file_service:
    port: 5003

llm:
  provider: ollama
  endpoint: http://127.0.0.1:11434
  default_model: qwen2.5:7b

paths:
  data: ./data
  skills: ./skills
  output: ./output

  🛠️ 开发指南

添加新技能
1.创建技能文件 skills/my_skill.py

2.实现 execute(self, params) 方法

3.创建技能声明 config/skills/my_skill.yaml

技能模板
class MySkill:
    name = "my_skill"
    description = "技能描述"
    version = "1.0.0"
    category = "category"
    
    def execute(self, params):
        # 实现逻辑
        return {"success": True, "result": "结果"}

skill = MySkill()

🐛 故障排查
问题	             解决方案
端口被占用   	 ./start.sh stop 后重新启动
服务启动失败	 查看 logs/ 目录下的日志
技能找不到	   检查 config/skills/ 中的 YAML 声明
LLM 无响应	   确认 Ollama 服务正在运行

📊 服务端口
服务	          端口	    URL
API Gateway	    5002	http://localhost:5002
文件服务	       5003	 http://localhost:5003
多智能体         5005	 http://localhost:5005
文档生成	       5008	 http://localhost:5008
Web Dashboard	  5011	http://localhost:5011

🤝 贡献
欢迎提交 Issue 和 Pull Request！

1.Fork 项目

2.创建功能分支 (git checkout -b feature/amazing)

3.提交更改 (git commit -m 'Add amazing feature')

4.推送到分支 (git push origin feature/amazing)

5.创建 Pull Request

📄 许可证
MIT License

<div align="center">
⭐ 如果觉得有用，请给个 Star！

Report Bug · Request Feature

</div> EOF