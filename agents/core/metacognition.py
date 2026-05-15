"""元认知模块 - 思考如何思考，学习如何学习"""

import json
import requests
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class Metacognition:
    """元认知：观察自己的学习过程，优化学习策略"""
    
    def __init__(self):
        self.meta_file = Path("data/metacognition.json")
        self._load()
    
    def _load(self):
        if self.meta_file.exists():
            with open(self.meta_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "learning_strategies": [],
                "effectiveness_history": [],
                "current_strategy": "balanced",
                "self_improvements": []
            }
    
    def _save(self):
        with open(self.meta_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def analyze_learning_effectiveness(self):
        """分析学习效果"""
        stats = brain.get_stats()
        
        analysis = {
            "learning_rate": stats['total_experiences'] / max(1, (datetime.now().timestamp() - 1747000000) / 3600),
            "success_trend": self._calculate_trend(),
            "knowledge_growth": stats['knowledge_graph_nodes'],
            "bottlenecks": self._identify_bottlenecks()
        }
        
        return analysis
    
    def _calculate_trend(self):
        """计算成功率趋势"""
        exps = brain.knowledge.get('experiences', [])[-50:]
        if len(exps) < 10:
            return "stable"
        
        recent = [e.get('result', {}).get('success', False) for e in exps[-10:]]
        older = [e.get('result', {}).get('success', False) for e in exps[-20:-10]]
        
        recent_rate = sum(recent) / len(recent)
        older_rate = sum(older) / len(older)
        
        if recent_rate > older_rate + 0.1:
            return "improving"
        elif recent_rate < older_rate - 0.1:
            return "declining"
        return "stable"
    
    def _identify_bottlenecks(self):
        """识别学习瓶颈"""
        bottlenecks = []
        
        # 检查是否有重复失败的模式
        exps = brain.knowledge.get('experiences', [])
        failures = [e for e in exps if not e.get('result', {}).get('success', False)]
        
        if len(failures) > len(exps) * 0.3:
            bottlenecks.append("失败率过高，需要调整策略")
        
        # 检查知识图谱增长
        if len(brain.knowledge.get('knowledge_graph', [])) < 10:
            bottlenecks.append("知识图谱增长缓慢")
        
        return bottlenecks
    
    def adjust_strategy(self):
        """动态调整学习策略"""
        analysis = self.analyze_learning_effectiveness()
        
        if analysis['success_trend'] == 'declining':
            new_strategy = "conservative"
            reason = "成功率下降，采用保守策略"
        elif analysis['bottlenecks']:
            new_strategy = "exploratory"
            reason = f"存在瓶颈: {analysis['bottlenecks'][0]}，增加探索"
        elif analysis['learning_rate'] < 0.5:
            new_strategy = "aggressive"
            reason = "学习速度慢，加速学习"
        else:
            new_strategy = "balanced"
            reason = "运行良好，保持平衡"
        
        if new_strategy != self.data['current_strategy']:
            self.data['current_strategy'] = new_strategy
            self.data['self_improvements'].append({
                "timestamp": datetime.now().isoformat(),
                "old_strategy": self.data['current_strategy'],
                "new_strategy": new_strategy,
                "reason": reason
            })
            self._save()
            
            brain.record_experience(
                agent="metacognition",
                action=f"策略调整: {new_strategy}",
                result={"success": True, "reason": reason},
                context="meta_learning"
            )
            
            print(f"🔄 学习策略调整: {new_strategy} - {reason}")
        
        return {"strategy": new_strategy, "reason": reason}
    
    def get_strategy(self):
        return self.data['current_strategy']

metacog = Metacognition()

if __name__ == '__main__':
    print("🧠 元认知分析:", metacog.analyze_learning_effectiveness())
    print("📊 策略调整:", metacog.adjust_strategy())
