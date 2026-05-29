"""LLM 驱动的目标生成器"""

import json
import requests
import re
from datetime import datetime
from typing import List, Dict

class LLMGoalGenerator:
    def __init__(self):
        self.goal_history = []
    
    def _call_llm(self, prompt: str) -> str:
        try:
            resp = requests.post(
                'http://localhost:5002/api/chat',
                json={'message': prompt, 'user_role': 'system'},
                timeout=config_helper.get_timeout("default")
            )
            return resp.json().get('response', '')
        except Exception as e:
            return f"LLM调用失败: {e}"
    
    def generate_goals(self, system_state: Dict, history: List) -> List[Dict]:
        context = f"""
系统状态:
- 技能: {system_state.get('skills', 0)}
- 健康: {system_state.get('health', 'unknown')}
- 记忆: {system_state.get('memory', 0)}

历史: {len(history)} 条记录

返回 JSON: {{"goals": [{{"description": "目标", "priority": "high", "steps": []}}]}}
"""
        response = self._call_llm(context)
        
        try:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return self._convert(data)
        except:
            pass
        
        return self._fallback()
    
    def _convert(self, data: Dict) -> List[Dict]:
        goals = []
        for g in data.get('goals', []):
            goals.append({
                "id": f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": g.get('description', ''),
                "priority": g.get('priority', 'medium'),
                "steps": g.get('steps', []),
                "source": "llm"
            })
        return goals
    
    def _fallback(self) -> List[Dict]:
        return [{
            "id": f"goal_fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "检查系统健康状态",
            "priority": "high",
            "steps": ["调用健康检查", "分析结果"],
            "source": "fallback"
        }]

llm_goal_gen = LLMGoalGenerator()
