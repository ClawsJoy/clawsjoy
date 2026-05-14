"""自适应学习器"""
import json
from pathlib import Path
from collections import deque
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class AdaptiveLearner:
    def __init__(self):
        self.success_window = deque(maxlen=50)
        self.adaptation_log = Path("logs/adaptation.log")
        self.state = {"mode": "balance", "confidence": 0.5}
    
    def update_state(self):
        stats = brain.get_stats()
        success_rate = stats.get('success_rate', 0.5)
        self.success_window.append(success_rate)
        
        if success_rate > 0.85:
            new_mode = "exploit"
        elif success_rate < 0.6:
            new_mode = "explore"
        else:
            new_mode = "balance"
        
        if new_mode != self.state["mode"]:
            with open(self.adaptation_log, 'a') as f:
                f.write(f"{datetime.now()}: {self.state['mode']} -> {new_mode}\n")
        
        self.state.update({"mode": new_mode, "success_rate": success_rate})
        return self.state

if __name__ == "__main__":
    learner = AdaptiveLearner()
    state = learner.update_state()
    print(f"📊 模式: {state['mode']}")
    print(f"📈 成功率: {state['success_rate']*100:.1f}%")
