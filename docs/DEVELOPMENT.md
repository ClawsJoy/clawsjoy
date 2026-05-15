#ClawsJoy 开发指南
#项目结构
clawsjoy/
├── agent_gateway_web.py   # API 网关
├── agents/                 # Agent 系统
│   ├── core/              # 核心 Agent
│   ├── custom/            # 自定义 Agent
│   └── multi/             # 多智能体协作
├── skills/                 # 原子技能
│   ├── core/              # 核心调度
│   ├── math/              # 数学计算
│   ├── image/             # 图像处理
│   ├── video/             # 视频制作
│   └── ...
├── lib/                    # 核心库
├── intelligence/           # 智能模块
├── web/                    # Web 界面
└── tests/                  # 单元测试
#添加新技能
1. 创建技能文件
# skills/my_skill.py
class MySkill:
    name = "my_skill"
    description = "技能描述"
    version = "1.0.0"
    category = "my_category"
    
    def execute(self, params):
        # 实现逻辑
        result = params.get("input", "default")
        return {"success": True, "result": result}

skill = MySkill()
#2. 注册技能
技能会被自动发现，无需手动注册。
#3. 测试技能
# 通过 API 测试
curl -X POST http://localhost:5002/api/skills/execute \
  -H "Content-Type: application/json" \
  -d '{"skill": "my_skill", "params": {"input": "test"}}'
添加新 Agent
# agents/custom/my_agent.py
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    name = "my_agent"
    description = "Agent 描述"
    capabilities = ["capability1", "capability2"]
    skills = ["skill1", "skill2"]
    
    def execute(self, params):
        operation = params.get("operation")
        if operation == "do_something":
            return self._do_something(params)
        return {"success": False, "error": "未知操作"}
    
    def _do_something(self, params):
        # 实现逻辑
        return {"success": True, "result": "done"}

my_agent = MyAgent()
#添加新 API 端点
# agent_gateway_web.py
@app.route('/api/my_endpoint', methods=['GET'])
def my_endpoint():
    return jsonify({"message": "Hello"})
#运行测试
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_core.py -v
代码规范
使用 PEP 8 风格

添加类型注解

编写文档字符串

单元测试覆盖核心功能
