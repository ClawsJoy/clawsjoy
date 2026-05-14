#!/usr/bin/env python3
"""
增强版大脑模块 - 完整的强化学习闭环
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

class EnhancedBrain:
    def __init__(self, brain_file: str = None):
        if brain_file is None:
            brain_file = Path(__file__).parent.parent / "data" / "enhanced_brain.json"
        self.brain_file = Path(brain_file)
        self.knowledge = self._load()
        print(f"🧠 增强大脑已激活")
        print(f"   📚 经验: {len(self.knowledge.get('experiences', []))} 条")
        print(f"   🏆 最佳实践: {len(self.knowledge.get('best_practices', []))} 条")
        print(f"   📊 成功率: {self.get_success_rate():.1%}")
    
    def _load(self) -> Dict:
        if self.brain_file.exists():
            try:
                return json.load(open(self.brain_file))
            except:
                pass
        return self._get_default()
    
    def _get_default(self) -> Dict:
        return {
            "experiences": [],
            "best_practices": [],
            "failures": [],
            "patterns": {},
            "stats": {
                "total_actions": 0,
                "successful": 0,
                "failed": 0,
                "last_learning": None,
                "learning_epochs": 0
            },
            "q_table": {}  # 强化学习 Q 表
        }
    
    def _save(self):
        self.brain_file.parent.mkdir(parents=True, exist_ok=True)
        json.dump(self.knowledge, open(self.brain_file, 'w'), indent=2)
    
    def record_experience(self, agent: str, action: str, result: Dict, context: str = "") -> Dict:
        """记录经验 - 触发学习"""
        exp_id = hashlib.sha256(f"{agent}{action}{datetime.now()}".encode()).hexdigest()[:8]
        
        experience = {
            "id": exp_id,
            "agent": agent,
            "action": action[:200],
            "result": result,
            "context": context[:500],
            "timestamp": datetime.now().isoformat(),
            "success": result.get('success', False),
            "reward": self._calculate_reward(result)
        }
        
        self.knowledge["experiences"].append(experience)
        self.knowledge["stats"]["total_actions"] += 1
        
        if experience["success"]:
            self.knowledge["stats"]["successful"] += 1
        else:
            self.knowledge["stats"]["failed"] += 1
        
        # 触发学习
        self._learn_from_experience(experience)
        
        # 保持最近500条
        if len(self.knowledge["experiences"]) > 500:
            self.knowledge["experiences"] = self.knowledge["experiences"][-500:]
        
        self._save()
        return experience
    
    def _calculate_reward(self, result: Dict) -> float:
        """计算奖励值"""
        reward = 1.0 if result.get('success', False) else -1.0
        
        # 额外奖励因素
        if result.get('quality', 0) > 0:
            reward += result.get('quality', 0) * 0.5
        if result.get('speed', 0) > 0:
            reward += result.get('speed', 0) * 0.3
        
        return max(-1.0, min(1.0, reward))
    
    def _learn_from_experience(self, experience: Dict):
        """从经验中学习"""
        agent = experience['agent']
        action = experience['action']
        reward = experience['reward']
        
        # 更新 Q 表
        state_key = f"{agent}_{hashlib.md5(action[:50].encode()).hexdigest()[:8]}"
        if state_key not in self.knowledge["q_table"]:
            self.knowledge["q_table"][state_key] = 0
        
        # Q-learning 更新
        alpha = 0.1  # 学习率
        current_q = self.knowledge["q_table"][state_key]
        self.knowledge["q_table"][state_key] = current_q + alpha * (reward - current_q)
        
        # 如果是成功经验，尝试提取模式
        if experience["success"] and reward > 0.5:
            self._extract_pattern(experience)
        
        # 如果是失败经验，记录错误模式
        if not experience["success"] and reward < -0.5:
            self._record_failure_pattern(experience)
    
    def _extract_pattern(self, experience: Dict):
        """提取成功模式"""
        agent = experience['agent']
        action = experience['action'][:100]
        
        pattern_key = f"{agent}_{hashlib.md5(action.encode()).hexdigest()[:8]}"
        
        if pattern_key not in self.knowledge["patterns"]:
            self.knowledge["patterns"][pattern_key] = {
                "action_pattern": action,
                "agent": agent,
                "success_count": 0,
                "confidence": 0.0
            }
        
        pattern = self.knowledge["patterns"][pattern_key]
        pattern["success_count"] += 1
        pattern["confidence"] = min(1.0, pattern["success_count"] / 10)
        
        # 高置信度模式自动成为最佳实践
        if pattern["confidence"] >= 0.8 and pattern["success_count"] >= 3:
            self.add_best_practice(action, agent, confidence=pattern["confidence"])
    
    def _record_failure_pattern(self, experience: Dict):
        """记录失败模式"""
        failure = {
            "id": experience['id'],
            "agent": experience['agent'],
            "action": experience['action'][:200],
            "error": experience['result'].get('error', 'unknown'),
            "timestamp": experience['timestamp'],
            "avoid_count": 0
        }
        self.knowledge["failures"].append(failure)
        
        # 保持最近100条失败
        if len(self.knowledge["failures"]) > 100:
            self.knowledge["failures"] = self.knowledge["failures"][-100:]
    
    def add_best_practice(self, practice: str, agent: str, confidence: float = 0.8, tags: list = None):
        """添加最佳实践"""
        # 检查是否已存在
        existing = [p for p in self.knowledge["best_practices"] 
                   if p.get('practice') == practice and p.get('agent') == agent]
        if existing:
            existing[0]["use_count"] += 1
            existing[0]["confidence"] = max(existing[0].get("confidence", 0), confidence)
        else:
            best_practice = {
                "practice": practice,
                "agent": agent,
                "tags": tags or [],
                "confidence": confidence,
                "use_count": 1,
                "created_at": datetime.now().isoformat()
            }
            self.knowledge["best_practices"].append(best_practice)
            print(f"   🏆 自动发现最佳实践: {practice[:60]}...")
        
        self._save()
    
    def get_best_practices(self, agent: str = None, min_confidence: float = 0.5, limit: int = 5) -> List[Dict]:
        """获取最佳实践（按置信度排序）"""
        practices = self.knowledge.get("best_practices", [])
        if agent:
            practices = [p for p in practices if p.get('agent') == agent]
        
        # 按置信度和使用次数排序
        practices.sort(key=lambda x: (x.get('confidence', 0), x.get('use_count', 0)), reverse=True)
        return practices[:limit]
    
    def get_advice(self, agent: str, action: str, context: str = "") -> Optional[Dict]:
        """为动作提供建议"""
        action_key = action[:100]
        
        # 1. 检查是否有相似的成功模式
        for pattern_id, pattern in self.knowledge.get("patterns", {}).items():
            if pattern.get('agent') == agent and pattern.get('confidence', 0) > 0.7:
                if pattern.get('action_pattern') in action_key or action_key in pattern.get('action_pattern', ''):
                    return {
                        "type": "pattern",
                        "message": f"建议使用类似模式: {pattern.get('action_pattern', '')[:100]}",
                        "confidence": pattern.get('confidence', 0.5)
                    }
        
        # 2. 检查是否有类似的失败需要避免
        for failure in self.knowledge.get("failures", []):
            if failure.get('agent') == agent:
                if failure.get('action') in action_key:
                    return {
                        "type": "warning",
                        "message": f"避免上次失败: {failure.get('error', 'unknown')}",
                        "confidence": 0.7
                    }
        
        # 3. 检查 Q 表
        state_key = f"{agent}_{hashlib.md5(action_key.encode()).hexdigest()[:8]}"
        q_value = self.knowledge["q_table"].get(state_key, 0)
        if q_value > 0.3:
            return {
                "type": "positive",
                "message": f"该动作历史表现良好 (Q={q_value:.2f})",
                "confidence": min(1.0, q_value)
            }
        elif q_value < -0.3:
            return {
                "type": "negative",
                "message": f"该动作历史表现不佳 (Q={q_value:.2f})",
                "confidence": min(1.0, -q_value)
            }
        
        return None
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        stats = self.knowledge.get("stats", {})
        total = stats.get('total_actions', 0)
        if total == 0:
            return 0.0
        return stats.get('successful', 0) / total
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.knowledge.get("stats", {})
        return {
            "total_experiences": len(self.knowledge.get("experiences", [])),
            "best_practices": len(self.knowledge.get("best_practices", [])),
            "patterns": len(self.knowledge.get("patterns", {})),
            "failures": len(self.knowledge.get("failures", [])),
            "success_rate": self.get_success_rate(),
            "q_table_size": len(self.knowledge.get("q_table", {})),
            "last_learning": stats.get('last_learning'),
            "learning_epochs": stats.get('learning_epochs', 0)
        }
    
    def learn_from_feedback(self, experience_id: str, is_good: bool, rating: int = 3):
        """从用户反馈学习"""
        for exp in self.knowledge.get("experiences", []):
            if exp.get('id') == experience_id:
                # 调整奖励
                old_reward = exp.get('reward', 0)
                new_reward = old_reward + (rating - 3) / 3.0
                exp['reward'] = max(-1.0, min(1.0, new_reward))
                
                # 重新学习
                self._learn_from_experience(exp)
                
                if is_good and rating >= 4:
                    self._extract_pattern(exp)
                elif not is_good and rating <= 2:
                    self._record_failure_pattern(exp)
                
                self._save()
                return True
        return False

# 创建全局实例
brain = EnhancedBrain()
