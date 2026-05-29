"""前端数据采集Agent - 通过注册中心注册"""
from core.agents.base.smart_agent import SmartAgent
from core.lib.agent_registry import agent_registry


class FrontendAgent(SmartAgent):
    """前端数据采集Agent"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        super().__init__("frontend_agent")
        print(f"📊 前端Agent v{self.VERSION} 初始化")
    
    def process(self, user_input: str, context=None):
        return {"response": "前端数据已采集", "success": True}
    
    def collect(self, data_type: str, data: dict):
        """采集前端数据"""
        return {"success": True, "type": data_type}


frontend_agent = FrontendAgent()
agent_registry.register("frontend_agent", {
    "name": "前端采集Agent",
    "type": "data_collector",
    "capabilities": ["frontend_metrics", "user_behavior", "error_tracking"],
    "enabled": True
})
print("✅ 前端Agent已注册到注册中心")
