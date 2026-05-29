"""决策 Agent - 完整版"""
from core.v5.agent.base import BaseAgent
from core.v5.llm.client import llm
from core.v5.memory.manager import MemoryManager
from typing import Dict
from datetime import datetime


class DecisionAgent(BaseAgent):
    """决策助手 - 完整功能"""
    
    def __init__(self, user_id: str = "default"):
        super().__init__("decision", user_id)
        self.mem_mgr = MemoryManager(user_id, "decision")
    
    def process(self, user_input: str) -> Dict:
        """处理决策请求"""
        self.update_stats()
        
        # 获取历史决策作为上下文
        context = self.mem_mgr.search_context(user_input, limit=3)
        context_text = "\n".join(context) if context else ""
        
        prompt = f"""你是专业的决策分析助手。

用户偏好: {self.mem_mgr.preferences}

历史相关决策: {context_text}

请分析以下问题，给出：
1. 问题分析
2. 可选方案 (至少2个)
3. 推荐方案
4. 理由
5. 风险等级 (高/中/低)
6. 优先级 (紧急/高/中/低)

用户问题: {user_input}

决策分析:"""
        
        response = llm.generate(prompt, model_type="decision")
        
        # 记录决策历史
        self.mem_mgr.add_conversation(user_input, response)
        self.record_history(user_input, response)
        
        return {
            "success": True,
            "type": "decision",
            "response": response,
            "user_id": self.user_id
        }
