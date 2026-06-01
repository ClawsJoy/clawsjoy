"""Orchestrator v6.0 - 集成原子引擎的智能路由器"""

from typing import Dict, Any, Optional
from engine.semantic import semantic_engine
from engine.profile import profile_engine
from engine.reasoning import reasoning_engine
from engine.planning import planning_engine

class OrchestratorV6:
    """智能路由 - 使用原子引擎增强决策"""
    
    def __init__(self, user_id: str = "anonymous"):
        self.user_id = user_id
        # Agent 映射
        self.agent_map = {
            'code': 'code_agent',
            '代码编写': 'code_agent',
            'weather': 'chat_agent',
            '天气查询': 'chat_agent',
            'translate': 'translate_agent',
            '翻译': 'translate_agent',
            'calculate': 'chat_agent',
            '计算': 'chat_agent',
            'greeting': 'chat_agent',
            '问候': 'chat_agent',
            'name_set': 'chat_agent',
            'name_query': 'chat_agent',
            'capability': 'chat_agent',
            '能力询问': 'chat_agent',
            'thanks': 'chat_agent',
            'farewell': 'chat_agent',
        }
     
    def smart_route(self, message: str) -> str:
        """智能路由 - 使用语义理解 + 推理"""
        # 1. 语义理解
        result = semantic_engine.understand(message)
        # IntentResult 对象: result.intent 是字符串, result.confidence 是浮点数
        intent = result.intent          # 直接取字符串，不是 result.intent.name
        confidence = result.confidence  # 直接取浮点数，不是 result.intent.confidence
    
        print(f"[OrchestratorV6] 语义理解: intent={intent}, conf={confidence}")

        # 2. 路由选择
        if confidence > 0.6 and intent in self.agent_map:
            target = self.agent_map[intent]
            print(f"[OrchestratorV6] 路由: {intent} → {target}")
            return target

        # 3. 默认路由
        print(f"[OrchestratorV6] 默认路由: chat_agent")
        return "chat_agent"

    
    def decompose_task(self, task: str) -> Dict:
        """任务分解 - 使用规划引擎"""
        # 使用语义理解获取意图
        result = semantic_engine.understand(task)
        intent = result.intent.name
        
        # 规划引擎分解
        plan = planning_engine.decompose(task, intent)
        
        return {
            'intent': intent,
            'plan_id': plan.id,
            'subtasks': [{'name': s.name, 'description': s.description, 'agent': s.agent} 
                        for s in plan.subtasks],
            'total_subtasks': len(plan.subtasks)
        }

# 全局实例
orchestrator_v6 = OrchestratorV6()
