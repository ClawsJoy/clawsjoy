#!/usr/bin/env python3
"""Knowledge Grower - Knowledge Grower 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
import re
from pathlib import Path
from datetime import datetime
from core.lib.smart_adapter import smart_adapter


class KnowledgeGrower:
    """知识自增长器"""
    
    def __init__(self):
        self.learned_file = Path("data/learned_knowledge.json")
        self._load_learned()
    
    def _load_learned(self):
        if self.learned_file.exists():
            with open(self.learned_file, 'r') as f:
                self.learned = json.load(f)
        else:
            self.learned = {"facts": [], "patterns": [], "insights": []}
            self._save()
    
    def _save(self):
        with open(self.learned_file, 'w') as f:
            json.dump(self.learned, f, indent=2)
    
    def learn_from_conversation(self, user_input: str, response: str):
        """从对话中学习"""
        # 简单提取：检测明显的知识陈述
        if "是" in user_input and len(user_input) > 10:
            fact = user_input.strip()
            self.learned["facts"].append({
                "fact": fact,
                "response": response[:100],
                "learned_at": datetime.now().isoformat()
            })
            self.learned["facts"] = self.learned["facts"][-100:]
            self._save()
            print(f"📚 学到新知识: {fact[:50]}...")
    
    def learn_from_success(self, goal: str, plan: list, result: str):
        """从成功执行中学习"""
        insight = {
            "goal": goal[:100],
            "plan": plan,
            "result": result[:200],
            "timestamp": datetime.now().isoformat()
        }
        self.learned["insights"].append(insight)
        self.learned["insights"] = self.learned["insights"][-50:]
        self._save()
        print(f"💡 获得新洞察: {goal[:50]}...")
    
    def get_stats(self) -> dict:
        return {
            "facts_count": len(self.learned["facts"]),
            "insights_count": len(self.learned["insights"]),
            "patterns_count": len(self.learned["patterns"])
        }
