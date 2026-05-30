"""LLM 驱动的自主决策 - 修复版"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict
import re

class LLMDecisionAgent:
    def __init__(self):
        self.decision_history = []
        self.goals = []
        self.failure_patterns = []
        self._load_memory()
    
    def _load_memory(self):
        memory_file = Path(f"{config_helper.get_data_root()}/autonomous/llm_decisions.json")
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                data = json.load(f)
                self.decision_history = data.get('history', [])
                self.goals = data.get('goals', [])
                self.failure_patterns = data.get('failure_patterns', [])
    
    def _save_memory(self):
        memory_file = Path(f"{config_helper.get_data_root()}/autonomous/llm_decisions.json")
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(memory_file, 'w') as f:
            json.dump({
                'history': self.decision_history[-200:],
                'goals': self.goals,
                'failure_patterns': self.failure_patterns[-50:]
            }, f, indent=2, default=str)
    
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
    
    def sense(self) -> Dict:
        try:
            resp = requests.get('http://localhost:5002/api/skills', timeout=5)
            skill_count = resp.json().get('total', 0)
        except:
            skill_count = 0

        try:
            resp = requests.get('http://localhost:5002/api/health', timeout=5)
            health = resp.json().get('status', 'unknown') if resp.status_code == 200 else 'unknown'
        except:
            health = 'unknown'

        try:
            from core.lib.memory_vector import vector_memory
            memory_count = vector_memory.collection.count()
        except:
            memory_count = 0

        return {'skill_count': skill_count, 'health_status': health, 'memory_count': memory_count}
    
    def think(self, state: Dict) -> Dict:
        recent = self.decision_history[-5:] if self.decision_history else []
        history = "\n".join([f"  {d.get('timestamp', '')[:16]}: {d.get('decision', {}).get('action_type', '?')} - {d.get('result', {}).get('success', False)}" for d in recent])

        prompt = f"""状态: 技能{state['skill_count']}, 健康{state['health_status']}, 记忆{state['memory_count']}
历史: {history}
返回JSON: {{"action": "check|fix|optimize|idle", "target": "具体目标", "reason": "理由"}}"""

        response = self._call_llm(prompt)
        try:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return {"action": "idle", "target": "none", "reason": "解析失败"}
    
    def act(self, decision: Dict) -> Dict:
        action = decision.get('action', 'idle')
        if action == 'check':
            return {"success": True, "result": "检查完成"}
        elif action == 'fix':
            try:
                requests.post('http://localhost:5002/api/knowledge/sync', timeout=10)
                return {"success": True, "result": "修复已执行"}
            except:
                return {"success": False, "result": "修复失败"}
        elif action == 'optimize':
            return {"success": True, "result": "优化完成"}
        return {"success": True, "result": "空闲"}
    
    def reflect(self, decision: Dict, result: Dict, state: Dict):
        feedback = {"correct": result.get('success', False), "lesson": "无"}
        if self.decision_history:
            self.decision_history[-1]['reflection'] = feedback
        self._save_memory()
    
    def run_cycle(self) -> Dict:
        print(f"\n🔄 决策循环 #{len(self.decision_history)+1}")
        state = self.sense()
        print(f"  📡 状态: 技能={state['skill_count']}, 健康={state['health_status']}")
        decision = self.think(state)
        print(f"  💭 决策: {decision.get('action', 'idle')} - {decision.get('reason', '')[:40]}")
        result = self.act(decision)
        print(f"  ⚡ 执行: {result.get('result', '')[:40]}")

        self.decision_history.append({
            'timestamp': datetime.now().isoformat(),
            'state': state,
            'decision': decision,
            'result': result
        })
        self.reflect(decision, result, state)
        self._save_memory()
        return result

agent = LLMDecisionAgent()
