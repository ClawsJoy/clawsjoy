"""智能决策引擎 - 基于LLM的自主决策"""
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class SmartDecisionEngine:
    """智能决策引擎 - 自主分析并做出决策"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.decision_history = []
        self.decision_file = Path("data/decisions.json")
        self.load_history()
        
    def load_history(self):
        if self.decision_file.exists():
            with open(self.decision_file, 'r') as f:
                self.decision_history = json.load(f)
    
    def save_history(self):
        with open(self.decision_file, 'w') as f:
            json.dump(self.decision_history[-100:], f, indent=2)
    
    def analyze_context(self) -> Dict:
        """分析当前上下文"""
        stats = brain.get_stats()
        
        context = {
            "timestamp": datetime.now().isoformat(),
            "system_stats": stats,
            "recent_decisions": self.decision_history[-5:],
            "available_agents": self._get_available_agents(),
            "success_rate": stats.get('success_rate', 0),
            "experience_level": stats.get('total_experiences', 0)
        }
        return context
    
    def _get_available_agents(self) -> List[str]:
        """获取可用Agent"""
        try:
            resp = requests.get("http://localhost:5005/agents", timeout=3)
            if resp.status_code == 200:
                return resp.json().get('agents', [])
        except:
            pass
        return ["SimpleLearningAgent", "SupervisorAgent"]
    
    def make_decision(self, question: str = None) -> Dict:
        """做出决策"""
        context = self.analyze_context()
        
        if question is None:
            # 自动决策：基于系统状态
            if context['success_rate'] < 0.7:
                question = "系统成功率偏低，应该采取什么措施？"
            elif context['experience_level'] < 30:
                question = "系统经验不足，如何快速学习？"
            else:
                question = "系统运行正常，如何进一步优化？"
        
        prompt = f"""
你是ClawsJoy的智能决策引擎。
当前系统状态:
{json.dumps(context, indent=2, ensure_ascii=False)}

用户问题: {question}

请做出决策，输出JSON格式:
{{
    "decision": "决策描述",
    "action": "具体行动",
    "confidence": 0-100,
    "reasoning": "决策理由"
}}
"""
        try:
            resp = requests.post(self.ollama_url, json={
                "model": "qwen2.5:7b",
                "prompt": prompt,
                "stream": False
            }, timeout=60)
            
            response = resp.json().get('response', '')
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1:
                decision = json.loads(response[start:end])
            else:
                decision = {"decision": "默认决策", "action": "继续监控", "confidence": 50}
            
            # 记录决策
            self.decision_history.append({
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "decision": decision
            })
            self.save_history()
            
            # 记录到大脑
            brain.record_experience(
                agent="decision_engine",
                action=decision.get('decision', 'unknown'),
                result={"confidence": decision.get('confidence', 0)},
                context=question
            )
            
            return decision
            
        except Exception as e:
            print(f"决策失败: {e}")
            return {"decision": "无法决策", "action": "保持现状", "confidence": 0}
    
    def auto_decide(self):
        """自动决策循环"""
        print("🧠 智能决策引擎启动")
        print("=" * 50)
        
        decision = self.make_decision()
        
        print(f"📋 问题: {decision.get('question', '系统状态分析')}")
        print(f"🎯 决策: {decision.get('decision', 'N/A')}")
        print(f"⚡ 行动: {decision.get('action', 'N/A')}")
        print(f"📊 置信度: {decision.get('confidence', 0)}%")
        print(f"💡 理由: {decision.get('reasoning', 'N/A')[:100]}")
        
        return decision

if __name__ == "__main__":
    engine = SmartDecisionEngine()
    engine.auto_decide()
