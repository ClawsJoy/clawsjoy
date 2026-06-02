# ClawsJoy Agent 注册开发指南

## 版本信息
- 版本: 2.0.0
- 更新日期: 2026-06-02
- 适用系统: ClawsJoy v5.0+

---

## 一、概述

ClawsJoy Agent 系统采用**三种注册机制并存**的设计：

1. **配置文件注册**：通过 `config/agents/registry/agents.yaml`
2. **工作区注册**：通过 `agents/{agent_name}/config.yaml`
3. **能力声明注册**：通过 `keywords.yaml` 的 `agent_capabilities`

---

## 二、Agent 架构
BaseAgent → SmartAgent → CodeAgent, ChatAgent, VideoAgent...

---

## 三、三种注册方式

### 3.1 工作区注册（推荐）
agents/code_agent/
├── config.yaml # Agent 配置
└── memory/ # 记忆存储

### 3.2 配置文件注册

`config/agents/registry/agents.yaml`

### 3.3 能力声明注册

`config/keywords.yaml` 中的 `agent_capabilities`

---

## 四、创建 Agent 类

```python
from core.agents.base.smart_agent import SmartAgent

class MyAgent(SmartAgent):
    name = "my_agent"
    description = "我的智能助手"
    
    def process(self, user_input: str, context=None) -> dict:
        return {"success": True, "response": "处理完成", "agent": self.name}
五、已注册的 Agent
Agent	类型	工作区
orchestrator	core	✅
code_agent	custom	✅
video_agent	custom	✅
vision_agent	custom	✅
translate_agent	custom	✅
...	...	...
六、常用命令
# 列出所有 Agent
curl http://localhost:5002/api/agents/list

# 热重载
curl -X POST http://localhost:5002/api/admin/agents/reload
本指南基于 ClawsJoy v5.0 实际验证
