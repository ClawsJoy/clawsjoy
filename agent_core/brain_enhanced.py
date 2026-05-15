#!/usr/bin/env python3
"""增强版大脑 v2 - 推理 + 知识迁移 + 类比学习（完整版）"""

import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import requests
import re

class EnhancedBrain:
    def __init__(self, brain_file: str = None):
        if brain_file is None:
            brain_file = Path(__file__).parent.parent / "data" / "brain_v2.json"
        self.brain_file = Path(brain_file)
        self.knowledge = self._load()
        self.ollama_url = "http://localhost:11434/api/generate"
        print(f"🧠 增强大脑 v2 已激活")
        print(f"   📚 经验: {len(self.knowledge.get('experiences', []))} 条")
        print(f"   🏆 最佳实践: {len(self.knowledge.get('best_practices', []))} 条")
        print(f"   🔗 知识图谱: {len(self.knowledge.get('knowledge_graph', []))} 个节点")
        print(f"   🎯 类比库: {len(self.knowledge.get('analogies', []))} 条")
    
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
            "knowledge_graph": [],
            "analogies": [],
            "skill_embeddings": {},
            "transfer_matrix": {},
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
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """获取文本向量"""
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
        return [hash(text) % 10000 / 10000 for _ in range(128)]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', text.lower())
        return [w for w in words if len(w) > 1][:10]
    
    def _calculate_reward(self, result: Dict) -> float:
        reward = 1.0 if result.get('success', False) else -1.0
        if result.get('quality', 0) > 0:
            reward += result.get('quality', 0) * 0.5
        if result.get('speed', 0) > 0:
            reward += result.get('speed', 0) * 0.3
        return max(-1.0, min(1.0, reward))
    
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
            "keywords": self._extract_keywords(action)
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
    
    def _update_knowledge_graph(self, experience: Dict):
        """更新知识图谱"""
        for kw in experience.get('keywords', []):
            # 查找或创建节点
            found = False
            for node in self.knowledge["knowledge_graph"]:
                if node.get('concept') == kw:
                    node['strength'] = node.get('strength', 1) + (0.2 if experience['success'] else -0.1)
                    node['strength'] = max(0.1, min(10.0, node['strength']))
                    if experience['id'] not in node.get('related_ids', []):
                        node.setdefault('related_ids', []).append(experience['id'])
                    found = True
                    break
            
            if not found:
                self.knowledge["knowledge_graph"].append({
                    "concept": kw,
                    "related_ids": [experience['id']],
                    "strength": 1.0,
                    "success_count": 1 if experience['success'] else 0,
                    "created_at": datetime.now().isoformat()
                })
    
    def _find_analogy(self, experience: Dict) -> Optional[str]:
        """查找类比经验"""
        best_match = None
        best_score = 0
        
        keywords = set(experience.get('keywords', []))
        
        for exp in self.knowledge["experiences"][-100:]:
            if exp['id'] == experience['id']:
                continue
            
            exp_keywords = set(exp.get('keywords', []))
            overlap = len(keywords & exp_keywords)
            score = overlap / max(len(keywords), len(exp_keywords)) if keywords else 0
            
            if score > best_score and score > 0.3:
                best_score = score
                best_match = exp['id']
        
        return best_match
    
    def add_best_practice(self, practice: str, agent: str, tags: list = None, confidence: float = 0.8):
        """添加最佳实践"""
        existing = [p for p in self.knowledge["best_practices"] 
                   if p.get('practice') == practice and p.get('agent') == agent]
        if existing:
            existing[0]["use_count"] = existing[0].get("use_count", 0) + 1
            existing[0]["confidence"] = max(existing[0].get("confidence", 0), confidence)
        else:
            self.knowledge["best_practices"].append({
                "practice": practice,
                "agent": agent,
                "tags": tags or [],
                "confidence": confidence,
                "use_count": 1,
                "created_at": datetime.now().isoformat()
            })
        self._save()
    
    def get_best_practices(self, agent: str = None, min_confidence: float = 0.5, limit: int = 5) -> List[Dict]:
        practices = self.knowledge.get("best_practices", [])
        if agent:
            practices = [p for p in practices if p.get('agent') == agent]
        practices.sort(key=lambda x: (x.get('confidence', 0), x.get('use_count', 0)), reverse=True)
        return practices[:limit]
    
    def infer_solution(self, problem: str) -> Dict:
        """推理解决方案"""
        self.knowledge["stats"]["inferences"] += 1
        self._save()
        
        problem_keywords = self._extract_keywords(problem)
        
        # 1. 基于关键词匹配经验
        best_match = None
        best_score = 0
        
        for exp in self.knowledge["experiences"][-200:]:
            if not exp.get('success'):
                continue
            
            exp_keywords = set(exp.get('keywords', []))
            overlap = len(set(problem_keywords) & exp_keywords)
            score = overlap / max(len(problem_keywords), len(exp_keywords)) if problem_keywords else 0
            
            if score > best_score and score > 0.2:
                best_score = score
                best_match = exp
        
        if best_match:
            return {
                "found": True,
                "type": "经验匹配",
                "confidence": best_score,
                "solution": best_match.get('action', ''),
                "source_id": best_match.get('id', '')
            }
        
        # 2. 基于知识图谱
        for kw in problem_keywords:
            for node in self.knowledge["knowledge_graph"]:
                if node.get('concept') == kw and node.get('strength', 0) > 0.5:
                    return {
                        "found": True,
                        "type": "知识图谱",
                        "confidence": min(1.0, node.get('strength', 0) / 5),
                        "solution": f"相关概念: {kw}",
                        "related_count": len(node.get('related_ids', []))
                    }
        
        # 无匹配时返回建议
        return {
            "found": False,
            "type": "无匹配",
            "suggestion": "请记录更多经验以便我学习",
            "solution": "暂无解决方案"
        }
    
    def transfer_knowledge(self, source_domain: str, target_domain: str) -> Dict:
        """知识迁移"""
        self.knowledge["stats"]["transfers"] += 1
        self._save()
        
        source_exps = [e for e in self.knowledge["experiences"] 
                       if source_domain in e.get('action', '').lower() and e.get('success')]
        
        if not source_exps:
            return {"success": False, "error": f"无 {source_domain} 领域经验"}
        
        transfer_key = f"{source_domain}->{target_domain}"
        if transfer_key not in self.knowledge["transfer_matrix"]:
            self.knowledge["transfer_matrix"][transfer_key] = {"count": 0, "examples": []}
        
        transfer = self.knowledge["transfer_matrix"][transfer_key]
        transfer["count"] += 1
        transfer["examples"].append({
            "source": source_exps[0].get('action', '')[:100],
            "target_domain": target_domain,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save()
        
        return {
            "success": True,
            "transferred_from": source_domain,
            "to": target_domain,
            "example": source_exps[0].get('action', '')[:100],
            "confidence": min(1.0, transfer["count"] / 10)
        }
    
    def learn_from_analogy(self, new_problem: str, known_solution: str) -> Dict:
        """类比学习"""
        self.knowledge["stats"]["analogies_used"] += 1
        self._save()
        
        analogy_id = hashlib.sha256(f"{new_problem}{datetime.now()}".encode()).hexdigest()[:8]
        self.knowledge["analogies"].append({
            "id": analogy_id,
            "problem": new_problem[:200],
            "analogy_to": known_solution[:200],
            "created_at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "analogy_id": analogy_id,
            "message": "已记录类比，下次遇到类似问题可参考"
        }
    
    def get_advice(self, agent: str, action: str) -> Optional[Dict]:
        """获取建议（兼容旧版）"""
        inference = self.infer_solution(action)
        if inference.get('found'):
            return {
                "type": "inference",
                "message": inference.get('solution', '')[:100],
                "confidence": inference.get('confidence', 0.5)
            }
        return None
    
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
            "analogies_used": stats.get("analogies_used", 0),
            "q_table_size": len(self.knowledge.get("transfer_matrix", {}))
        }

# 全局实例
brain = EnhancedBrain()
