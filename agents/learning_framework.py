#!/usr/bin/env python3
"""统一学习框架 - 轻量级，不需要海量数据"""

import json
from pathlib import Path
from datetime import datetime

class LearningFramework:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.knowledge_file = Path(f"/mnt/d/clawsjoy/data/knowledge/{agent_name}_learned.json")
        self.load()
    
    def load(self):
        if self.knowledge_file.exists():
            with open(self.knowledge_file) as f:
                self.knowledge = json.load(f)
        else:
            self.knowledge = {
                "learned": [],
                "success_rate": 0,
                "last_learned": None
            }
    
    def save(self):
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def learn(self, new_item, source):
        """学习新知识"""
        self.knowledge["learned"].append({
            "item": new_item,
            "source": source,
            "learned_at": datetime.now().isoformat()
        })
        self.save()
        print(f"📚 {self.agent_name} 学习了: {new_item}")
    
    def record_feedback(self, item, success):
        """记录反馈"""
        for learned in self.knowledge["learned"]:
            if learned["item"] == item:
                learned["success"] = success
                break
        # 更新成功率
        successes = sum(1 for l in self.knowledge["learned"] if l.get("success", False))
        total = len(self.knowledge["learned"])
        self.knowledge["success_rate"] = successes / total if total > 0 else 0
        self.save()
