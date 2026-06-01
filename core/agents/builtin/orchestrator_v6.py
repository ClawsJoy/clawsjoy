"""Orchestrator v6.0 - 集成原子引擎的智能路由器"""

from typing import Dict, Any, Optional
from engine.semantic import semantic_engine
from engine.reasoning import reasoning_engine

class OrchestratorV6:
    """智能路由 - 使用原子引擎增强决策"""

    def __init__(self, user_id: str = "anonymous"):
        self.user_id = user_id
        self.agent_map = {
            'script': 'youtube_agent',
            '生成脚本': 'youtube_agent',
            '写脚本': 'youtube_agent',
            '视频脚本': 'youtube_agent',
            'code': 'code_agent',
            '代码编写': 'code_agent',
            'script': 'youtube_agent',
            '生成脚本': 'youtube_agent',
            '写脚本': 'youtube_agent',
            '视频脚本': 'youtube_agent',
            'director': 'director_agent',
            '导演': 'director_agent',
            '策划': 'director_agent',
            '导演策划': 'director_agent',
            '内容日历': 'director_agent',
            '日历': 'director_agent',
            '排期': 'director_agent',
            '生产状态': 'director_agent',
            '进度': 'director_agent',
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
            'thanks': 'chat_agent',
            'farewell': 'chat_agent',
        }

    def smart_route(self, message: str) -> str:
        """智能路由 - 使用语义理解"""
        try:
            result = semantic_engine.understand(message)
            intent = result.intent
            confidence = result.confidence

            if confidence > 0.6 and intent in self.agent_map:
                target = self.agent_map[intent]
                print(f"[OrchestratorV6] {intent}({confidence:.2f}) → {target}")
                return target
        except Exception as e:
            print(f"[OrchestratorV6] 错误: {e}")

        return "chat_agent"

    def decompose_task(self, task: str) -> Dict:
        """任务分解"""
        result = semantic_engine.understand(task)
        intent = result.intent
        return {
            'intent': intent,
            'subtasks': []
        }

orchestrator_v6 = OrchestratorV6()
