#!/usr/bin/env python3
"""智能体学习模块 - 让智能体能够学习和成长"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class AgentLearner:
    """智能体学习器 - 从经验中学习"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.root = Path("/mnt/d/clawsjoy_clean")
        self.experience_file = self.root / "data/experience/learning_log.json"
        self.patterns_file = self.root / "data/experience/success_patterns.json"
        self.examples_file = self.root / "data/training/few_shot_examples.json"
        
        self._load_data()
    
    def _load_data(self):
        """加载学习数据"""
        try:
            if self.experience_file.exists():
                with open(self.experience_file) as f:
                    self.data = json.load(f)
            else:
                self.data = {"interactions": [], "skills_performance": {}, "user_preferences": {}}
            
            if self.patterns_file.exists():
                with open(self.patterns_file) as f:
                    self.patterns = json.load(f)
            else:
                self.patterns = {"patterns": []}
        except Exception as e:
            logger.error(f"加载学习数据失败: {e}")
            self.data = {"interactions": [], "skills_performance": {}, "user_preferences": {}}
            self.patterns = {"patterns": []}
    
    def _save_data(self):
        """保存学习数据"""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.experience_file, 'w') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def record_interaction(self, user_input: str, skill: str, params: Dict, 
                           success: bool, response: str, llm_analyzed: bool = True):
        """记录一次交互，用于学习"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input[:200],
            "skill": skill,
            "params": params,
            "success": success,
            "response": response[:200],
            "llm_analyzed": llm_analyzed
        }
        
        self.data["interactions"].append(interaction)
        
        # 只保留最近 1000 条
        if len(self.data["interactions"]) > 1000:
            self.data["interactions"] = self.data["interactions"][-1000:]
        
        # 更新技能表现
        if skill not in self.data["skills_performance"]:
            self.data["skills_performance"][skill] = {"success": 0, "fail": 0, "total": 0}
        
        if success:
            self.data["skills_performance"][skill]["success"] += 1
        else:
            self.data["skills_performance"][skill]["fail"] += 1
        self.data["skills_performance"][skill]["total"] += 1
        
        self._save_data()
    
    def get_skill_performance(self, skill: str) -> Dict:
        """获取技能表现"""
        return self.data["skills_performance"].get(skill, {"success": 0, "fail": 0, "total": 0})
    
    def get_best_skills(self, limit: int = 5) -> List[Dict]:
        """获取表现最好的技能"""
        skills = []
        for name, perf in self.data["skills_performance"].items():
            if perf["total"] > 0:
                rate = perf["success"] / perf["total"]
                skills.append({"skill": name, "success_rate": rate, "total": perf["total"]})
        
        skills.sort(key=lambda x: x["success_rate"], reverse=True)
        return skills[:limit]
    
    def get_skills_need_improvement(self, limit: int = 5) -> List[Dict]:
        """获取需要改进的技能"""
        skills = []
        for name, perf in self.data["skills_performance"].items():
            if perf["total"] > 5:  # 至少有5次尝试
                rate = perf["success"] / perf["total"]
                if rate < 0.7:
                    skills.append({"skill": name, "success_rate": rate, "total": perf["total"]})
        
        skills.sort(key=lambda x: x["success_rate"])
        return skills[:limit]
    
    def update_patterns(self, user_input: str, skill: str, success: bool):
        """从成功经验中学习模式"""
        # 提取关键词
        keywords = user_input[:50]
        
        # 检查是否已有类似模式
        for pattern in self.patterns.get("patterns", []):
            if pattern["skill"] == skill:
                pattern["usage_count"] += 1
                if success:
                    # 更新成功率
                    total = pattern.get("usage_count", 1)
                    current_rate = pattern.get("success_rate", 0.5)
                    pattern["success_rate"] = (current_rate * (total - 1) + (1 if success else 0)) / total
                break
        else:
            # 新模式
            self.patterns["patterns"].append({
                "pattern": keywords[:50],
                "skill": skill,
                "confidence": 0.5,
                "usage_count": 1,
                "success_rate": 1.0 if success else 0.0
            })
        
        self.patterns["last_updated"] = datetime.now().isoformat()
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict:
        """获取学习统计"""
        total = len(self.data["interactions"])
        skills_count = len(self.data["skills_performance"])
        
        success_total = sum(p["success"] for p in self.data["skills_performance"].values())
        fail_total = sum(p["fail"] for p in self.data["skills_performance"].values())
        
        return {
            "total_interactions": total,
            "skills_used": skills_count,
            "total_success": success_total,
            "total_fail": fail_total,
            "overall_success_rate": success_total / (success_total + fail_total) if (success_total + fail_total) > 0 else 0,
            "best_skills": self.get_best_skills(3),
            "needs_improvement": self.get_skills_need_improvement(3)
        }
    
    def get_report(self) -> str:
        """生成学习报告"""
        stats = self.get_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    智能体学习报告                                 ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  总交互次数: {stats['total_interactions']}                                 ║
║  使用技能数: {stats['skills_used']}                                         ║
║  总成功率: {stats['overall_success_rate']*100:.1f}%                                 ║
║                                                                  ║
║  最佳技能:                                                       ║
"""
        for s in stats['best_skills']:
            report += f"║    ✅ {s['skill']}: {s['success_rate']*100:.0f}% ({s['total']}次)                    ║\n"
        
        if stats['needs_improvement']:
            report += f"║                                                                  ║\n"
            report += f"║  需要改进:                                                       ║\n"
            for s in stats['needs_improvement']:
                report += f"║    ⚠️ {s['skill']}: {s['success_rate']*100:.0f}% ({s['total']}次)                    ║\n"
        
        report += f"║                                                                  ║\n"
        report += f"╚══════════════════════════════════════════════════════════════════╝"
        
        return report


agent_learner = AgentLearner()


if __name__ == "__main__":
    print(agent_learner.get_report())
