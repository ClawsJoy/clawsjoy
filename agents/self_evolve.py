#!/usr/bin/env python3
"""Agent 自进化 - 根据执行结果优化自己"""

import json
from pathlib import Path
from datetime import datetime

class SelfEvolve:
    def __init__(self):
        self.memory_file = Path("data/agent_memory.json")
        self.load_memory()
    
    def load_memory(self):
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                self.memory = json.load(f)
        else:
            self.memory = {"skills": {}, "workflows": [], "feedback": []}
    
    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def record_execution(self, skill, success, duration, context):
        """记录执行结果，用于优化"""
        if skill not in self.memory["skills"]:
            self.memory["skills"][skill] = {"success": 0, "fail": 0, "avg_duration": 0}
        
        stats = self.memory["skills"][skill]
        if success:
            stats["success"] += 1
        else:
            stats["fail"] += 1
        
        stats["avg_duration"] = (stats["avg_duration"] * (stats["success"] + stats["fail"] - 1) + duration) / (stats["success"] + stats["fail"])
        
        self.save_memory()
    
    def get_best_skill_for_task(self, task_type):
        """根据历史数据，推荐最佳技能"""
        # 简单实现：返回成功率最高的技能
        best = None
        best_rate = 0
        for skill, stats in self.memory["skills"].items():
            total = stats["success"] + stats["fail"]
            if total > 0:
                rate = stats["success"] / total
                if rate > best_rate:
                    best_rate = rate
                    best = skill
        return best
    
    def learn_from_feedback(self, user_input, action, satisfied):
        """从用户反馈学习"""
        self.memory["feedback"].append({
            "input": user_input,
            "action": action,
            "satisfied": satisfied,
            "time": datetime.now().isoformat()
        })
        self.save_memory()

if __name__ == "__main__":
    evolve = SelfEvolve()
    
    # 模拟记录
    evolve.record_execution("spider", True, 2.5, "采集香港新闻")
    evolve.record_execution("promo", True, 30, "制作视频")
    evolve.record_execution("youtube", False, 5, "上传失败")
    
    print(f"推荐技能: {evolve.get_best_skill_for_task('content')}")
    print(json.dumps(evolve.memory, ensure_ascii=False, indent=2))
