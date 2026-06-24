"""业务 Agent 基类 v2 - 集成横向引擎能力"""

from typing import Dict, Any, Optional
from core.agents.business.base_business_agent import BusinessAgent


class BusinessAgentV2(BusinessAgent):
    """业务 Agent 基类 - 集成原子引擎"""
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._init_engines()
    
    def _init_engines(self):
        """初始化横向引擎（子类可覆盖）"""
        self.engines = {}
        self._init_semantic()
        self._init_knowledge()
        self._init_reasoning()
    
    def _init_semantic(self):
        try:
            from engine.semantic import semantic_engine
            self.engines["semantic"] = semantic_engine
        except Exception as e:
            pass
    
    def _init_knowledge(self):
        try:
            from engine.knowledge import knowledge_engine
            self.engines["knowledge"] = knowledge_engine
        except Exception as e:
            pass
    
    def _init_reasoning(self):
        try:
            from engine.reasoning import reasoning_engine
            self.engines["reasoning"] = reasoning_engine
        except Exception as e:
            pass
    
    def get_engine(self, name: str):
        return self.engines.get(name)
    
    def call_engine(self, name: str, method: str, *args, **kwargs):
        """调用引擎方法"""
        engine = self.get_engine(name)
        if engine and hasattr(engine, method):
            return getattr(engine, method)(*args, **kwargs)
        return None
