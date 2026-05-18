"""Agent 模板 - 新 Agent 开发指南"""

from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    """
    Agent 模板示例
    
    必须实现:
    - name: Agent 名称
    - description: Agent 描述
    - capabilities: 能力列表
    - execute(): 执行方法
    """
    
    name = "my_agent"
    description = "我的 Agent"
    version = "1.0.0"
    type = "custom"
    
    capabilities = [
        {
            "name": "example_capability",
            "description": "示例能力",
            "skills": ["skill_name"]
        }
    ]
    
    def __init__(self):
        super().__init__(
            agent_id="my_agent",
            config={
                "name": "我的Agent",
                "type": "custom",
                "personality": "professional"
            }
        )
    
    def execute(self, params):
        """
        执行任务
        
        Args:
            params: 任务参数
            
        Returns:
            dict: 执行结果
        """
        # 记录开始
        self.remember(f"开始执行: {params}")
        
        try:
            # 业务逻辑
            result = self._do_something(params)
            
            # 记录成功
            self.remember(f"执行成功: {result}")
            return {"success": True, "result": result}
            
        except Exception as e:
            # 记录失败
            self.remember(f"执行失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _do_something(self, params):
        """具体业务逻辑"""
        # TODO: 实现业务逻辑
        return {"message": "Hello World"}

# 创建全局实例
my_agent = MyAgent()
