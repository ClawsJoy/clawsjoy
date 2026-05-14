#!/usr/bin/env python3
"""增强版大脑 v2 - 推理 + 知识迁移 + 类比学习"""

import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import requests

class EnhancedBrainV2:
    def __init__(self, brain_file: str = None):
        if brain_file is None:
            brain_file = Path(__file__).parent.parent / "data" / "brain_v2.json"
        self.brain_file = Path(brain_file)
        self.knowledge = self._load()
        self.ollama_url = "http://localhost:11434/api/generate"
        print(f"🧠 增强大脑 v2 已激活")
        print(f"   📚 经验: {len(self.knowledge.get('experiences', []))} 条")
        print(f"   🏆 最佳实践: {len(self.knowledge.get('best_practices', []))} 条")
        print(f"   🔗 知识图谱: {len(self.knowledge.get('knowledge_graph', []))} 个关联")
    
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
            "knowledge_graph": [],      # 新增：知识图谱
            "analogies": [],            # 新增：类比库
            "skill_embeddings": {},     # 新增：技能向量
            "transfer_matrix": {},      # 新增：迁移矩阵
            "stats": {
                "total_actions": 0,
                "successful": 0,
                "failed": 0,
                "inferences": 0,
                "transfers": 0,
                "analogies_used": 0
            }
        }
    
    def _save(self):
        self.brain_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.brain_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def record_experience(self, agent: str, action: str, result: Dict, context: str = "") -> Dict:
        """记录经验，同时更新知识图谱"""
        exp_id = hashlib.sha256(f"{agent}{action}{datetime.now()}".encode()).hexdigest()[:8]
        
        experience = {
            "id": exp_id,
            "agent": agent,
            "action": action[:200],
            "result": result,
            "context": context[:500],
            "timestamp": datetime.now().isoformat(),
            "success": result.get('success', False),
            "reward": self._calculate_reward(result),
            "embedding": self._get_text_embedding(action)  # 新增：向量化
        }
        
        self.knowledge["experiences"].append(experience)
        self.knowledge["stats"]["total_actions"] += 1
        
        if experience["success"]:
            self.knowledge["stats"]["successful"] += 1
        else:
            self.knowledge["stats"]["failed"] += 1
        
        # 更新知识图谱
        self._update_knowledge_graph(experience)
        
        # 查找类比
        analogy = self._find_analogy(experience)
        if analogy:
            self.knowledge["analogies"].append({
                "source": exp_id,
                "target": analogy,
                "similarity": 0.7,
                "created_at": datetime.now().isoformat()
            })
        
        self._save()
        return experience
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """获取文本向量（用于相似度计算）"""
        try:
            resp = requests.post(
                f"{self.ollama_url}",
                json={"model": "nomic-embed-text", "prompt": text[:500], "stream": False},
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get('embedding', [])
        except:
            pass
        # 降级：简单哈希向量
        return [hash(text) % 10000 / 10000 for _ in range(384)]
    
    def _update_knowledge_graph(self, experience: Dict):
        """更新知识图谱 - 建立概念关联"""
        action_words = experience['action'].lower().split()[:10]
        
        for word in action_words:
            if len(word) > 3:
                # 查找相关概念
                for existing in self.knowledge["knowledge_graph"]:
                    if word in existing.get('concept', ''):
                        # 增加关联强度
                        existing['strength'] = existing.get('strength', 1) + 0.1
                        break
                else:
                    # 新概念
                    self.knowledge["knowledge_graph"].append({
                        "concept": word,
                        "related_actions": [experience['id']],
                        "success_count": 1 if experience['success'] else 0,
                        "strength": 1.0
                    })
    
    def _find_analogy(self, experience: Dict) -> Optional[str]:
        """查找类比经验"""
        best_match = None
        best_score = 0
        
        for exp in self.knowledge["experiences"][-100:]:
            if exp['id'] == experience['id']:
                continue
            
            # 简单相似度：共享关键词
            words1 = set(experience['action'].lower().split())
            words2 = set(exp['action'].lower().split())
            overlap = len(words1 & words2)
            score = overlap / max(len(words1), len(words2))
            
            if score > best_score and score > 0.3:
                best_score = score
                best_match = exp['id']
        
        return best_match
    
    def _calculate_reward(self, result: Dict) -> float:
        reward = 1.0 if result.get('success', False) else -1.0
        if result.get('quality', 0) > 0:
            reward += result.get('quality', 0) * 0.5
        return max(-1.0, min(1.0, reward))
    
    def infer_solution(self, problem: str) -> Optional[Dict]:
        """推理解决方案 - 基于经验和类比"""
        self.knowledge["stats"]["inferences"] += 1
        
        # 1. 基于关键词匹配
        problem_lower = problem.lower()
        best_match = None
        best_score = 0
        
        for exp in self.knowledge["experiences"][-200:]:
            if not exp['success']:
                continue
            
            # 关键词重叠度
            exp_words = set(exp['action'].lower().split())
            prob_words = set(problem_lower.split())
            overlap = len(exp_words & prob_words)
            score = overlap / max(len(exp_words), len(prob_words))
            
            if score > best_score and score > 0.2:
                best_score = score
                best_match = exp
        
        if best_match:
            return {
                "found": True,
                "type": "direct_match",
                "confidence": best_score,
                "solution": best_match['action'],
                "source_id": best_match['id']
            }
        
        # 2. 基于知识图谱推理
        for concept in problem_lower.split():
            if len(concept) > 3:
                for node in self.knowledge["knowledge_graph"]:
                    if concept in node['concept']:
                        return {
                            "found": True,
                            "type": "graph_inference",
                            "confidence": node['strength'] / 10,
                            "solution": f"相关概念: {node['concept']}",
                            "related_actions": node.get('related_actions', [])[:3]
                        }
        
        return {"found": False}
    
    def transfer_knowledge(self, source_domain: str, target_domain: str) -> Dict:
        """知识迁移 - 从一个领域迁移到另一个领域"""
        self.knowledge["stats"]["transfers"] += 1
        
        # 查找源领域的成功经验
        source_exps = [e for e in self.knowledge["experiences"] 
                       if source_domain in e['action'].lower() and e['success']]
        
        if not source_exps:
            return {"success": False, "error": f"No experience in {source_domain}"}
        
        # 记录迁移
        transfer_key = f"{source_domain}->{target_domain}"
        if transfer_key not in self.knowledge["transfer_matrix"]:
            self.knowledge["transfer_matrix"][transfer_key] = {
                "count": 0,
                "success_rate": 0,
                "examples": []
            }
        
        transfer = self.knowledge["transfer_matrix"][transfer_key]
        transfer["count"] += 1
        transfer["examples"].append({
            "source": source_exps[0]['action'],
            "target_domain": target_domain,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save()
        
        return {
            "success": True,
            "transferred_from": source_domain,
            "to": target_domain,
            "example": source_exps[0]['action'][:100],
            "confidence": min(1.0, transfer["count"] / 10)
        }
    
    def learn_from_analogy(self, new_problem: str, known_solution: str) -> Dict:
        """类比学习 - 用已知解决类似问题"""
        self.knowledge["stats"]["analogies_used"] += 1
        
        # 记录类比
        analogy_id = hashlib.sha256(f"{new_problem}{datetime.now()}".encode()).hexdigest()[:8]
        self.knowledge["analogies"].append({
            "id": analogy_id,
            "problem": new_problem[:200],
            "analogy_to": known_solution[:200],
            "created_at": datetime.now().isoformat()
        })
        
        self._save()
        
        return {
            "success": True,
            "analogy_id": analogy_id,
            "message": f"已记录类比: 新问题 → 已知方案"
        }
    
    def get_stats(self) -> Dict:
        stats = self.knowledge.get("stats", {})
        return {
            "total_experiences": len(self.knowledge.get("experiences", [])),
            "best_practices": len(self.knowledge.get("best_practices", [])),
            "knowledge_graph_nodes": len(self.knowledge.get("knowledge_graph", [])),
            "analogies": len(self.knowledge.get("analogies", [])),
            "transfers": stats.get("transfers", 0),
            "inferences": stats.get("inferences", 0),
            "success_rate": stats.get("successful", 0) / max(1, stats.get("total_actions", 1)),
            "analogies_used": stats.get("analogies_used", 0)
        }

brain_v2 = EnhancedBrainV2()
