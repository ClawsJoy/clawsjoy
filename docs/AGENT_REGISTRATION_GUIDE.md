# ClawsJoy Agent 注册开发指南

## 版本信息
- 版本: 1.0.0
- 更新日期: 2026-05-27
- 适用系统: ClawsJoy v5.0+

---

## 一、概述

ClawsJoy Agent 系统采用**配置驱动 + 静态继承**的设计哲学。开发者只需：

1. 创建 Agent 类（继承 `SmartAgent`）
2. 在配置文件中声明
3. 系统自动发现并注册

**无需修改核心代码，无需重启服务（支持热重载）**

---

## 二、Agent 架构
┌─────────────────────────────────────────────────────────────┐
│ ClawsJoy Agent 体系 │
├─────────────────────────────────────────────────────────────┤
│ │
│ BaseAgent (基础能力) │
│ ├── 用户隔离 (user_id) │
│ ├── 记忆系统 (remember/recall) │
│ ├── 配置管理 (_config) │
│ └── 生命周期钩子 (on_init, on_start, on_stop) │
│ ↑ │
│ │ 继承 │
│ │ │
│ SmartAgent (智能能力) │
│ ├── 任务分解 (_decompose_task) │
│ ├── 工具调用 (_execute_subtask) │
│ ├── 自我反思 (_reflect) │
│ └── 配置驱动 (smart_config) │
│ ↑ │
│ │ 继承 │
│ │ │
│ CodeAgent, ChatAgent, DecisionAgent... (具体 Agent) │
│ │
└─────────────────────────────────────────────────────────────┘

---

## 三、快速开始

### 3.1 创建 Agent 类

```python
# core/agents/my_agent.py

from core.agents.smart_agent import SmartAgent


class MyAgent(SmartAgent):
    """我的自定义 Agent"""
    
    name = "my_agent"                    # Agent 唯一标识
    description = "我的智能助手"          # 描述
    type = "custom"                      # core / custom / marketplace
    version = "1.0.0"                    # 版本号

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_my_config()

    def _load_my_config(self):
        """加载自定义配置"""
        import yaml
        from pathlib import Path
        config_file = Path("config/agents/my_agent.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.my_config = yaml.safe_load(f)

    def process(self, user_input: str, context: dict = None) -> dict:
        """处理用户输入 - 必须实现"""
        # 使用基类的智能处理
        result = self.smart_process(user_input, context)
        
        return {
            "success": result.get("success", True),
            "response": result.get("response", "处理完成"),
            "agent": self.name,
            "user_id": self.user_id
        }


# 全局实例（必需）
my_agent = MyAgent()
3.2 注册 Agent
在 config/agents.yaml 中添加配置：
agents:
  my_agent:
    name: "我的智能助手"
    type: "custom"
    enabled: true
    module: "core.agents.my_agent"
    class: "MyAgent"
    capabilities:
      - custom_capability_1
      - custom_capability_2
3.3 配置说明
字段	类型	必填	说明
name	string	是	显示名称
type	string	是	core/custom/marketplace
enabled	boolean	是	是否启用
module	string	是	Python 模块路径
class	string	是	Agent 类名
capabilities	list	否	能力声明
四、使用 Agent
4.1 API 调用
# 发送消息到 Agent
curl -X POST http://localhost:5002/api/agent/my_agent/message \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "user_id": "test"}'

# 响应
{
  "success": true,
  "response": "你好！有什么可以帮您的？",
  "agent": "my_agent",
  "user_id": "test"
}
4.2 列出所有 Agent
curl http://localhost:5002/api/agents/list
4.3 Agent 间通信
from lib.agent_bus import get_bus

bus = get_bus()
bus.publish("my_agent", "topic.event", {"data": "value"})
五、高级特性
5.1 继承 SmartAgent 获得的能力
能力	方法	说明
任务分解	_decompose_task()	自动将复杂任务拆解为子任务
工具调用	_execute_subtask()	调用原子技能执行子任务
自我反思	_reflect()	失败时分析原因并调整策略
配置驱动	smart_config	通过 YAML 配置行为
5.2 记忆系统
# 存储记忆
self.remember("用户偏好", "喜欢简洁回答")

# 召回记忆
memories = self.recall("用户偏好", n=5)
5.3 技能调用
from lib.skill_loader_v3 import skill_loader

result = skill_loader.execute("skill_name", params)
六、热重载
修改配置后，系统自动检测并重新加载：
# 修改 config/agents.yaml 后
# 系统会自动检测变化并重新注册

# 或手动触发
curl -X POST http://localhost:5002/api/admin/agents/reload
七、示例：创建一个完整的 Agent
7.1 需求
创建一个天气助手，用户可以说"今天天气怎么样"
7.2 实现
# core/agents/weather_agent.py

from core.agents.smart_agent import SmartAgent
from lib.skill_loader_v3 import skill_loader


class WeatherAgent(SmartAgent):
    name = "weather_agent"
    description = "天气助手"
    type = "custom"
    version = "1.0.0"

    def process(self, user_input: str, context: dict = None) -> dict:
        # 调用天气技能
        result = skill_loader.execute("weather", {"city": self._extract_city(user_input)})
        
        return {
            "success": True,
            "response": result.get("result", "获取天气失败"),
            "agent": self.name,
            "user_id": self.user_id
        }
    
    def _extract_city(self, text: str) -> str:
        # 简单提取城市名
        import re
        match = re.search(r'([\u4e00-\u9fa5]{2,3})天气', text)
        return match.group(1) if match else "北京"


weather_agent = WeatherAgent()
7.3 注册
# config/agents.yaml
agents:
  weather_agent:
    name: "天气助手"
    type: "custom"
    enabled: true
    module: "core.agents.weather_agent"
    class: "WeatherAgent"
    capabilities: ["weather_query"]
7.4 测试
curl -X POST http://localhost:5002/api/agent/weather_agent/message \
  -d '{"message": "上海天气怎么样"}'
八、常见问题
Q1: Agent 没有被加载？
检查清单：
1.config/agents.yaml 中 enabled: true

2.module 和 class 路径正确

3.Python 文件语法正确

4.类名与配置一致
Q2: Agent 返回空响应？
检查：
1.process 方法是否返回包含 response 字段的字典

2.是否调用了 super().__init__(user_id)

3.查看网关日志 tail -50 logs/gateway.log
Q3: 如何调试 Agent？
# 在 Agent 中添加日志
self.log(f"处理: {user_input}")
self.log(f"结果: {result}")
九、最佳实践
1.命名规范：Agent 名使用小写加下划线（如 my_agent）

2.单一职责：一个 Agent 专注一个领域

3.使用技能：具体功能实现为原子技能，Agent 负责编排

4.配置驱动：可变参数放到配置文件

5.错误处理：process 方法必须 try-except
十、参考
BaseAgent: core/agents/base_agent.py

SmartAgent: core/agents/smart_agent.py

Agent 配置: config/agents.yaml

API 文档: docs/API.md
本指南基于 ClawsJoy v5.0 编写，遵循配置驱动设计哲学

说明书已创建，包含：
- 架构设计
- 快速开始
- 配置说明
- API 使用
- 高级特性
- 完整示例
- 常见问题
- 最佳实践
