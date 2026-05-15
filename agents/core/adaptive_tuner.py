from lib.unified_config import config
"""自适应调优器 - 根据运行状态自动优化参数"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class AdaptiveTuner:
    def __init__(self):
        self.tuning_history = Path("data/tuning_history.json")
        self._load_history()
    
    def _load_history(self):
        if self.tuning_history.exists():
            with open(self.tuning_history, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {"tunings": [], "current_params": {}}
    
    def _save_history(self):
        with open(self.tuning_history, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def analyze_performance(self):
        """分析当前性能"""
        # 获取近期成功率
        stats = brain.get_stats()
        success_rate = stats.get('success_rate', 0.8)
        
        # 获取响应时间
        import requests
        try:
            start = __import__('time').time()
            requests.get('http://localhost:5002/api/health', timeout=5)
            response_time = __import__('time').time() - start
        except:
            response_time = 1.0
        
        # 获取系统负载
        result = subprocess.run("uptime | awk -F'load average:' '{print $2}'", 
                                shell=True, capture_output=True, text=True)
        load = result.stdout.strip()
        
        return {
            "success_rate": success_rate,
            "response_time": response_time,
            "system_load": load,
            "timestamp": datetime.now().isoformat()
        }
    
    def suggest_params(self, performance):
        """建议参数调整"""
        suggestions = []
        
        # 根据成功率调整
        if performance['success_rate'] < 0.7:
            suggestions.append({
                "param": "model_temperature",
                "current": 0.7,
                "suggested": 0.5,
                "reason": "成功率低，降低温度提高确定性"
            })
        
        if performance['response_time'] > 2.0:
            suggestions.append({
                "param": "max_tokens",
                "current": 2048,
                "suggested": 1024,
                "reason": "响应慢，减少最大 token"
            })
        
        if performance['success_rate'] > 0.9 and performance['response_time'] < 1.0:
            suggestions.append({
                "param": "model_temperature",
                "current": 0.7,
                "suggested": 0.9,
                "reason": "性能良好，增加温度提高创造力"
            })
        
        return suggestions
    
    def apply_tuning(self, suggestions):
        """应用调优"""
        results = []
        for s in suggestions:
            print(f"🔧 调优 {s['param']}: {s['current']} -> {s['suggested']} ({s['reason']})")
            
            # 这里实际修改配置
            self.history['current_params'][s['param']] = s['suggested']
            
            results.append({
                "param": s['param'],
                "old": s['current'],
                "new": s['suggested'],
                "reason": s['reason']
            })
            
            # 记录到大脑
            brain.record_experience(
                agent="adaptive_tuner",
                action=f"调优_{s['param']}",
                result={"success": True, "old": s['current'], "new": s['suggested']},
                context=s['reason']
            )
        
        self.history['tunings'].append({
            "timestamp": datetime.now().isoformat(),
            "changes": results,
            "performance": self.analyze_performance()
        })
        self._save_history()
        
        return results
    
    def tune(self):
        """执行一次调优"""
        print("\n" + "="*50)
        print("🎛️ 自适应调优")
        print("="*50)
        
        performance = self.analyze_performance()
        print(f"📊 性能: 成功率={performance['success_rate']:.1%}, 响应时间={performance['response_time']:.2f}s")
        
        suggestions = self.suggest_params(performance)
        
        if not suggestions:
            print("✅ 无需调优")
            return {"tuned": False}
        
        results = self.apply_tuning(suggestions)
        print(f"✅ 已调优 {len(results)} 个参数")
        
        return {"tuned": True, "changes": results}

tuner = AdaptiveTuner()

if __name__ == '__main__':
    tuner.tune()
