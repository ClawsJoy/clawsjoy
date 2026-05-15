import sys
sys.path.insert(0, "/mnt/d/clawsjoy")
#!/usr/bin/env python3
"""自适应参数优化 - 基于反馈自动调整"""
import json
from lib.memory_simple import memory

class AdaptiveOptimizer:
    def __init__(self):
        self.params = self.load_params()
    
    def load_params(self):
        """加载当前参数"""
        import json
        from pathlib import Path
        param_file = Path("data/adaptive_params.json")
        if param_file.exists():
            with open(param_file) as f:
                return json.load(f)
        return {
            "target_duration": 60,
            "script_length": 200,
            "quality_threshold": 70,
            "learning_rate": 0.3
        }
    
    def save_params(self):
        import json
        from pathlib import Path
        Path("data").mkdir(exist_ok=True)
        with open("data/adaptive_params.json", 'w') as f:
            json.dump(self.params, f, indent=2)
    
    def optimize(self):
        """根据反馈优化参数"""
        outcomes = memory.recall_all(category='workflow_outcome')[-50:]
        success = len([o for o in outcomes if '成功' in o])
        rate = success / len(outcomes) * 100 if outcomes else 50
        
        # 自适应调整
        if rate < 40:
            self.params['quality_threshold'] = max(50, self.params['quality_threshold'] - 10)
            self.params['target_duration'] = max(30, self.params['target_duration'] - 10)
        elif rate > 80:
            self.params['quality_threshold'] = min(90, self.params['quality_threshold'] + 5)
            self.params['target_duration'] = min(120, self.params['target_duration'] + 10)
        
        self.params['learning_rate'] = 0.3 + (rate - 50) / 100
        
        self.save_params()
        
        memory.remember(
            f"参数优化|成功率:{rate:.0f}%|新参数:{self.params}",
            category="param_optimization"
        )
        return self.params

if __name__ == "__main__":
    optimizer = AdaptiveOptimizer()
    new_params = optimizer.optimize()
    print(f"优化后参数: {new_params}")
