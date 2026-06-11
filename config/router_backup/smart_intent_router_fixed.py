"""智能意图路由器 - 修复版"""

from typing import Dict
import re

class SmartIntentRouter:
    """智能路由器 - 简化可靠版"""
    
    # 意图关键词映射
    INTENT_KEYWORDS = {
        "math": ["计算", "等于", "+", "-", "*", "/", "多少", "数字", "求和"],
        "code": ["代码", "函数", "写一个", "python", "程序", "实现", "def"],
        "logic": ["推理", "如果", "那么", "因为", "所以", "逻辑", "怕水"],
        "translate": ["翻译", "translate", "中文", "英文"],
        "story": ["故事", "小说", "童话", "寓言"],
        "chat": ["你好", "谢谢", "怎么样", "什么是"]
    }
    
    def route(self, message: str) -> Dict:
        """路由消息到对应意图"""
        message_lower = message.lower()
        
        # 关键词匹配
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    return {
                        "intent": intent,
                        "confidence": 0.8,
                        "agent": self._get_agent_for_intent(intent)
                    }
        
        # 模式匹配
        if re.search(r'\d+[\+\-\*/]\d+', message):
            return {"intent": "math", "confidence": 0.9, "agent": "calculator_agent"}
        
        if re.search(r'def\s+\w+', message):
            return {"intent": "code", "confidence": 0.9, "agent": "code_agent"}
        
        # 默认
        return {"intent": "chat", "confidence": 0.5, "agent": "chat_agent"}
    
    def _get_agent_for_intent(self, intent: str) -> str:
        """获取意图对应的 Agent"""
        agent_map = {
            "math": "calculator_agent",
            "code": "code_agent",
            "logic": "chat_agent",
            "translate": "translate_agent",
            "story": "chat_agent",
            "chat": "chat_agent"
        }
        return agent_map.get(intent, "chat_agent")

smart_intent_router = SmartIntentRouter()
