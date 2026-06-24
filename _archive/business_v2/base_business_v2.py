"""业务层基类 v2 - 用于执行业务任务（有 engines，可调用 LLM）"""

from typing import Dict, Optional
from core.agents.business.business_agent_v2 import BusinessAgentV2


class BusinessLayerAgent(BusinessAgentV2):
    """
    业务层智能体基类
    
    特点：
    - 继承 BusinessAgentV2，拥有 engines（semantic/knowledge/reasoning）
    - 可以直接调用 SmartAdapter 生成内容
    - 用于执行具体业务任务：分析、写作、翻译等
    """
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._init_smart_adapter()
    
    def _init_smart_adapter(self):
        """初始化智能适配器"""
        try:
            from core.lib.smart_adapter import smart_adapter
            self.smart_adapter = smart_adapter
        except Exception as e:
            print(f"[{self.name}] SmartAdapter 初始化失败: {e}")
            self.smart_adapter = None
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成内容（业务层专用）"""
        if self.smart_adapter:
            return self.smart_adapter.generate(prompt, auto_select=True, **kwargs)
        return "生成服务不可用"
    
    def process(self, user_input: str, context: Dict = None) -> Dict:
        """业务处理（子类实现）"""
        raise NotImplementedError


class OrchestrationLayerAgent(BusinessAgentV2):
    """
    编排层智能体基类
    
    特点：
    - 继承 BusinessAgentV2
    - 不直接调用 LLM，只做任务编排
    - 调度业务层 Agent
    """
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._agent_cache = {}
    
    def _get_business_agent(self, agent_name: str, user_id: str):
        """获取业务层 Agent 实例"""
        cache_key = f"{agent_name}:{user_id}"
        if cache_key not in self._agent_cache:
            try:
                module = __import__(f"agents.{agent_name}.agent", fromlist=[agent_name])
                for attr in dir(module):
                    if attr.endswith("Agent") and "Layer" not in attr:
                        agent_class = getattr(module, attr)
                        self._agent_cache[cache_key] = agent_class(user_id)
                        break
            except Exception as e:
                print(f"[{self.name}] 加载 Agent 失败 {agent_name}: {e}")
                return None
        return self._agent_cache[cache_key]
    
    def orchestrate(self, task: str, context: Dict = None) -> Dict:
        """编排任务（子类实现）"""
        raise NotImplementedError


class DecisionLayerAgent(BusinessAgentV2):
    """
    决策层智能体基类
    
    特点：
    - 使用推理引擎做决策
    - 不直接调用 LLM 生成内容
    - 决定路由到哪个 Agent
    """
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
    
    def decide(self, user_input: str, context: Dict = None) -> Dict:
        """决策（子类实现）"""
        raise NotImplementedError
