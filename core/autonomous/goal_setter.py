"""自主目标设定器 - 最终版"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class GoalSetter:
    def __init__(self):
        self.goals = []
        self.completed_goals = []
        self.failed_goals = []
        self.action_stats = {}
        self._load()
    
    def _load(self):
        goal_file = Path(f"{config_helper.get_data_root()}/autonomous/goals.json")
        if goal_file.exists():
            with open(goal_file, 'r') as f:
                data = json.load(f)
                self.goals = data.get('active', [])
                self.completed_goals = data.get('completed', [])
                self.failed_goals = data.get('failed', [])
                self.action_stats = data.get('stats', {})
    
    def _save(self):
        goal_file = Path(f"{config_helper.get_data_root()}/autonomous/goals.json")
        goal_file.parent.mkdir(exist_ok=True)
        with open(goal_file, 'w') as f:
            json.dump({
                'active': self.goals,
                'completed': self.completed_goals,
                'failed': self.failed_goals,
                'stats': self.action_stats,
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
    
    def generate_goals(self) -> List[Dict]:
        goals = []
        goals.append({
            "id": f"goal_check_skills_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "description": "检查所有技能的健康状态",
            "action": "check_skills",
            "priority": "high"
        })
        goals.append({
            "id": f"goal_sync_kb_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "description": "同步知识库到向量存储",
            "action": "sync_knowledge",
            "priority": "medium"
        })
        return goals
    
    def generate_advanced_goals(self) -> List[Dict]:
        goals = []
        try:
            resp = requests.get('http://localhost:5002/api/skills', timeout=5)
            skill_count = resp.json().get('total', 0)
        except:
            skill_count = 0

        if skill_count < 150:
            goals.append({
                "id": f"goal_fix_skills_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "description": "修复加载失败的技能",
                "action": "fix_broken_skills",
                "priority": "high"
            })

        goals.append({
            "id": f"goal_clean_cache_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "description": "清理系统缓存",
            "action": "clean_cache",
            "priority": "low"
        })

        goals.append({
            "id": f"goal_generate_report_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "description": "生成系统报告",
            "action": "generate_report",
            "priority": "low"
        })

        return goals
    
    def generate_proactive_goals(self) -> List[Dict]:
        goals = []
        goals.append({
            "id": f"goal_optimize_kb_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "description": "优化知识库索引",
            "action": "optimize_knowledge_base",
            "priority": "medium"
        })
        goals.append({
            "id": f"goal_defrag_memory_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "description": "整理向量记忆碎片",
            "action": "defrag_memory",
            "priority": "low"
        })
        goals.append({
            "id": f"goal_analyze_usage_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "description": "分析技能使用频率",
            "action": "analyze_skill_usage",
            "priority": "low"
        })
        return goals
    
    def add_goal(self, goal: Dict):
        for existing in self.goals:
            if existing['description'] == goal['description']:
                return
        self.goals.append(goal)
        self._sort_by_priority()
        self._save()
        print(f"🎯 新目标: {goal['description']}")
    
    def _sort_by_priority(self):
        priority_order = {"high": 0, "medium": 1, "low": 2}
        self.goals.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
    
    def get_next_goal(self) -> Dict:
        if not self.goals:
            return None
        self._sort_by_priority()
        return self.goals[0]
    
    def complete_goal(self, goal_id: str, result: Dict):
        for i, g in enumerate(self.goals):
            if g['id'] == goal_id:
                g['completed_at'] = datetime.now().isoformat()
                g['result'] = result
                self.completed_goals.append(g)
                self.goals.pop(i)
                action = g.get('action', 'unknown')
                if action not in self.action_stats:
                    self.action_stats[action] = {"total": 0, "success": 0}
                self.action_stats[action]["total"] += 1
                self.action_stats[action]["success"] += 1
                self._save()
                print(f"✅ 完成: {g['description']}")
                return True
        return False
    
    def fail_goal(self, goal_id: str, error: str):
        for i, g in enumerate(self.goals):
            if g['id'] == goal_id:
                g['failed_at'] = datetime.now().isoformat()
                g['error'] = error
                self.failed_goals.append(g)
                self.goals.pop(i)
                action = g.get('action', 'unknown')
                if action not in self.action_stats:
                    self.action_stats[action] = {"total": 0, "success": 0}
                self.action_stats[action]["total"] += 1
                self._save()
                print(f"❌ 失败: {g['description']}")
                return True
        return False
    
    def get_stats(self) -> Dict:
        total = len(self.completed_goals) + len(self.failed_goals)
        success = len(self.completed_goals)
        return {
            "active": len(self.goals),
            "completed": success,
            "failed": len(self.failed_goals),
            "success_rate": success / total if total > 0 else 0,
            "action_stats": self.action_stats
        }

goal_setter = GoalSetter()
