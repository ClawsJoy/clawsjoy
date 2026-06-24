"""标准化决策者 - 接收/输出标准化 JSON v1.0"""

import json
from typing import Dict, Any
from datetime import datetime
import uuid

from core.agents.business.business_agent_v2 import BusinessAgentV2
from core.lib.unified_intent_parser import unified_parser


class StandardDecisionAgent(BusinessAgentV2):
    """标准化决策者 - 多源决策"""
    
    name = "decision_agent"
    description = "标准化决策者 - 接收标准化 JSON，输出标准化 JSON"
    version = "1.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🎖️ 标准化决策者 v{self.version} 已启动")
    
    def execute(self, standard_json: Dict[str, Any]) -> Dict[str, Any]:
        """执行决策，输入输出都是标准化 JSON"""
        
        action = standard_json.get("action", "chat")
        target = standard_json.get("target", "text")
        keywords = standard_json.get("keywords", [])
        confidence = standard_json.get("confidence", 0.5)
        
        # 决策逻辑
        decision = {
            "should_delegate": True,
            "delegate_to": self._route_agent(action, target),
            "confidence": confidence,
            "reason": f"识别到意图: {action}_{target}"
        }
        
        # 更新标准化 JSON
        standard_json["decision"] = decision
        standard_json["status"] = "processing"
        standard_json["next"] = "continue"
        
        return standard_json
    
    def _route_agent(self, action: str, target: str) -> str:
        """路由到具体 Agent"""
        route_map = {
            ("play", "media"): "media_agent",
            ("search", "info"): "search_agent", 
            ("generate", "code"): "code_agent",
            ("generate", "image"): "vision_agent",
            ("schedule", "task"): "butler",
            ("translate", "text"): "translate_agent",
            ("calculate", "number"): "calculator_agent",
            ("chat", "text"): "chat_agent"
        }
        return route_map.get((action, target), "chat_agent")
    
    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        """业务入口（兼容旧接口）"""
        # 如果是字符串，先解析
        if isinstance(user_input, str):
            standard_json = unified_parser.parse(user_input, self.user_id)
        else:
            standard_json = user_input
        
        return self.execute(standard_json)


# 全局实例
decision_agent = StandardDecisionAgent()


def get_decision_agent(user_id: str = "default"):
    return StandardDecisionAgent(user_id)
