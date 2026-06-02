
## 2. 更新 Agent 注册指南

```bash
cd /home/flybo/clawsjoy_v5

echo "=========================================="
echo "基于实际系统更新 AGENT_REGISTRATION_GUIDE.md"
echo "=========================================="

# 备份原文件
cp docs/AGENT_REGISTRATION_GUIDE.md docs/AGENT_REGISTRATION_GUIDE.md.bak

# 更新内容
cat > docs/AGENT_REGISTRATION_GUIDE.md << 'EOF'
# ClawsJoy Agent 注册开发指南

## 版本信息
- 版本: 2.0.0
- 更新日期: 2026-06-02
- 适用系统: ClawsJoy v5.0+

---

## 一、概述

#ClawsJoy Agent 系统采用**三种注册机制并存**的设计：

1. **配置文件注册**：通过 `config/agents/registry/agents.yaml`
2. **工作区注册**：通过 `agents/{agent_name}/config.yaml`
3. **能力声明注册**：通过 `keywords.yaml` 的 `agent_capabilities`

#系统自动发现并注册 Agent，**无需修改核心代码，支持热重载**。

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
│ └── 生命周期钩子 │
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
│ CodeAgent, ChatAgent, VideoAgent... (具体 Agent) │
│ │
└─────────────────────────────────────────────────────────────┘

---

## 三、三种注册方式

### 3.1 方式一：工作区注册（推荐）

**目录结构：**
#agents/
├── code_agent/
│ ├── config.yaml # Agent 配置
│ ├── memory/ # 记忆存储
│ └── skills/ # 专属技能
├── video_agent/
│ └── config.yaml
└── ...

**配置文件示例 (`agents/code_agent/config.yaml`)：**
```yaml
agent:
  name: code_agent
  display_name: 代码助手
  type: builtin
  enabled: true
  role:
    title: "代码工程师"
    responsibilities:
      - "生成代码"
      - "代码审查"
  llm:
    provider: ollama
    model: deepseek-coder:6.7b
    temperature: 0.2
  capabilities:
    - write_code
    - debug_code
  keywords:
    - "写代码"
    - "编程"
    - "python"
###3.2 方式二：配置文件注册
#文件位置： config/agents/registry/agents.yaml
#agents:
  orchestrator:
    name: "任务编排器"
    type: "core"
    capabilities: ["task_planning", "skill_orchestration"]
    personality: "professional"
  
  code_agent:
    name: "代码助手"
    type: "custom"
    capabilities: ["code_generation", "code_review"]
###3.3 方式三：能力声明注册
#文件位置： config/keywords.yaml
agent_capabilities:
  code_agent:
    capable_of:
      - "写代码"
      - "编程"
      - "python"
      - "java"
    priority: 30
    requires_context: false
  
  video_agent:
    capable_of:
      - "剪辑"
      - "视频"
      - "制作"
    priority: 25
    requires_context: false
##四、创建 Agent 类
###4.1 基本模板
# core/agents/builtin/my_agent.py

from core.agents.base.smart_agent import SmartAgent
from typing import Dict, Optional


class MyAgent(SmartAgent):
    """我的自定义 Agent"""
    
    name = "my_agent"
    description = "我的智能助手"
    type = "custom"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🤖 {self.name} 初始化完成")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理用户输入 - 必须实现"""
        msg = user_input.lower()
        
        # 意图识别
        if "帮助" in msg:
            return self._show_help()
        
        # 调用技能
        result = self._call_skill("some_skill", {"input": user_input})
        
        return {
            "success": True,
            "response": result.get("result", "处理完成"),
            "agent": self.name,
            "user_id": self.user_id
        }
    
    def _show_help(self) -> Dict:
        return {"success": True, "response": "我可以帮你...", "agent": self.name}
    
    def _call_skill(self, skill_name: str, params: dict) -> dict:
        from core.lib.skill_loader_v3 import skill_loader
        return skill_loader.execute(skill_name, params)


# 注意：工作区注册方式不需要全局实例
###4.2 关键要点
#要素	要求   	说明
#继承	SmartAgent	获得智能能力
#name	字符串	Agent 唯一标识
#description	字符串	功能描述
#process	方法	必须实现
#全局实例	可选	工作区方式不需要
##五、注册 Agent
###5.1 工作区方式（最简单）
#创建目录：agents/my_agent/
#创建 config.yaml
#系统自动发现
# 系统启动时自动扫描
#agents/my_agent/
├── config.yaml
└── memory/
###5.2 配置文件方式
#编辑 config/agents/registry/agents.yaml，添加 Agent 信息后重启。
##六、使用 Agent
###6.1 API 调用
# 通过 Orchestrator 自动路由
#curl -X POST http://localhost:5002/api/v5/enhanced/chat \
#  -H "Content-Type: application/json" \
 # -d '{"message": "帮我写代码", "user_id": "test"}'

# 直接调用特定 Agent
#curl -X POST http://localhost:5002/api/agent/code_agent/message \
  -H "Content-Type: application/json" \
  -d '{"message": "写个Python函数", "user_id": "test"}'
###6.2 响应格式
{
  "success": true,
  "agent": "code_agent",
  "response": "这是生成的代码...",
  "user_id": "test"
}
##七、已注册的 Agent 列表
#Agent	类型	能力	工作区
#orchestrator	core	任务编排	✅
#code_agent	custom	代码生成	✅
#video_agent	custom	视频处理	✅
#vision_agent	custom	图像识别	✅
#translate_agent	custom	翻译	✅
#memory_agent	custom	记忆	✅
#chat_agent	core	对话	✅
#...	...	...	...
##八、热重载
# 修改配置后自动检测，或手动触发
#curl -X POST http://localhost:5002/api/admin/agents/reload
##九、常见问题
#Q1: Agent 没有被加载？
#检查清单：
#工作区目录是否存在？
#config.yaml 中 enabled: true？
#类名与配置一致？
#查看日志：tail -50 logs/error.log
#Q2: Agent 路由不到？
#检查：
#keywords.yaml 中是否有 agent_capabilities 声明？
#关键词是否匹配？
#优先级是否设置？
##十、最佳实践
#单一职责：一个 Agent 专注一个领域
#使用技能：具体功能实现为原子技能
#能力声明：在 keywords.yaml 中声明能力
#配置驱动：可变参数放到配置文件
#错误处理：process 方法必须 try-except
#附录：常用命令
# 列出所有 Agent
#curl http://localhost:5002/api/agents/list
# 查看 Agent 能力
#curl http://localhost:5002/api/agents/capabilities
# 热重载
#curl -X POST http://localhost:5002/api/admin/agents/reload
#本指南基于 ClawsJoy v5.0 实际验证，反映当前系统实现
EOF

echo "✅ Agent 注册指南已更新"

echo ""
echo "=========================================="
echo "两份手册已更新完成"
echo "=========================================="
ls -la docs/OPENCLAW_SKILL_SPECIFICATION.md
ls -la docs/AGENT_REGISTRATION_GUIDE.md