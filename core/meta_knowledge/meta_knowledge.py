#!/usr/bin/env python3
"""Meta Knowledge - Meta Knowledge 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class MetaKnowledge:
    """
    元知识管理 - 系统自省能力
    
    记录:
    1. 系统有哪些能力
    2. 能力之间的关系
    3. 能力的使用模式
    4. 能力的成功率
    """
    
    def __init__(self):
        self.meta_file = Path("data/meta_knowledge.json")
        self._load()
    
    def _load(self):
        if self.meta_file.exists():
            with open(self.meta_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "capabilities": {},
                "relationships": [],
                "usage_patterns": [],
                "success_patterns": [],
                "missing_gaps": [],
                "created_at": datetime.now().isoformat()
            }
            self._save()
    
    def _save(self):
        with open(self.meta_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def register_capability(self, name: str, category: str, description: str):
        """注册能力"""
        if name not in self.data["capabilities"]:
            self.data["capabilities"][name] = {
                "category": category,
                "description": description,
                "usage_count": 0,
                "success_count": 0,
                "success_rate": 0,
                "first_seen": datetime.now().isoformat(),
                "last_used": None
            }
            self._save()
            return True
        return False
    
    def record_usage(self, name: str, success: bool):
        """记录使用结果"""
        if name in self.data["capabilities"]:
            cap = self.data["capabilities"][name]
            cap["usage_count"] += 1
            if success:
                cap["success_count"] += 1
            cap["success_rate"] = cap["success_count"] / cap["usage_count"]
            cap["last_used"] = datetime.now().isoformat()
            self._save()
            return True
        return False
    
    def record_pattern(self, pattern: dict):
        """记录成功模式"""
        self.data["success_patterns"].append({
            **pattern,
            "timestamp": datetime.now().isoformat()
        })
        # 保留最近100条
        self.data["success_patterns"] = self.data["success_patterns"][-100:]
        self._save()
    
    def get_capabilities_summary(self) -> dict:
        """获取能力摘要"""
        caps = self.data["capabilities"]
        return {
            "total": len(caps),
            "by_category": self._group_by_category(),
            "high_success": [n for n, c in caps.items() 
                           if c.get("success_rate", 0) > 0.8],
            "needs_improvement": [n for n, c in caps.items() 
                                 if c.get("success_rate", 1) < 0.5 and c.get("usage_count", 0) > 5]
        }
    
    def _group_by_category(self) -> dict:
        categories = {}
        for name, cap in self.data["capabilities"].items():
            cat = cap.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    def find_similar_pattern(self, goal: str) -> Optional[Dict]:
        """查找相似的成功模式"""
        for pattern in self.data["success_patterns"]:
            goal_pattern = pattern.get("goal", "")
            if goal_pattern and len(set(goal.split()) & set(goal_pattern.split())) > 2:
                return pattern
        return None
