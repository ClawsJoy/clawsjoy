"""联邦学习模块 - Agent 间知识共享"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import threading


class FederatedLearning:
    """联邦学习管理器"""
    
    def __init__(self, storage_dir: str = "data/federated"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 知识库
        self._knowledge_base: Dict[str, Dict] = {}
        self._agent_knowledge: Dict[str, List[Dict]] = defaultdict(list)
        self._learning_rounds = 0
        
        # 锁
        self._lock = threading.Lock()
        
        # 加载已有知识
        self._load_knowledge()
        
        print(f"🤝 联邦学习模块已初始化")
        print(f"   📚 知识库大小: {len(self._knowledge_base)}")
    
    def share_knowledge(self, agent_name: str, knowledge: Dict, confidence: float = 0.8):
        """Agent 分享知识"""
        with self._lock:
            knowledge_id = f"{agent_name}_{datetime.now().timestamp()}"
            
            self._agent_knowledge[agent_name].append({
                "id": knowledge_id,
                "knowledge": knowledge,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            })
            
            # 合并到全局知识库
            self._merge_knowledge(agent_name, knowledge, confidence)
            
            # 保存
            self._save_knowledge()
            
            print(f"📤 [{agent_name}] 分享了 {len(knowledge)} 条知识")
    
    def _merge_knowledge(self, agent_name: str, knowledge: Dict, confidence: float):
        """合并知识到全局库"""
        for key, value in knowledge.items():
            if key not in self._knowledge_base:
                self._knowledge_base[key] = {
                    "value": value,
                    "sources": {agent_name: confidence},
                    "avg_confidence": confidence,
                    "updated_at": datetime.now().isoformat()
                }
            else:
                # 更新置信度
                sources = self._knowledge_base[key]["sources"]
                sources[agent_name] = confidence
                
                # 计算平均置信度
                avg_conf = sum(sources.values()) / len(sources)
                self._knowledge_base[key]["avg_confidence"] = avg_conf
                self._knowledge_base[key]["updated_at"] = datetime.now().isoformat()
    
    def query_knowledge(self, agent_name: str, query: str, top_k: int = 5) -> List[Dict]:
        """查询知识"""
        results = []
    
        for key, data in self._knowledge_base.items():
            # 改进匹配逻辑
            key_lower = key.lower()
            query_lower = query.lower()
        
            # 完全匹配
            if query_lower in key_lower or key_lower in query_lower:
                score = 1.0
            # 部分匹配
            else:
                query_words = set(query_lower.split())
                key_words = set(key_lower.split())
                common = query_words & key_words
                if common:
                    score = len(common) / max(len(query_words), len(key_words))
                else:
                    score = 0
        
            if score > 0.3:  # 阈值
                results.append({
                    "key": key,
                    "value": data["value"],
                    "confidence": data["avg_confidence"],
                    "score": score,
                    "sources": list(data["sources"].keys())
                })
    
        # 按综合分数排序
        results.sort(key=lambda x: (x["score"], x["confidence"]), reverse=True)
    
        print(f"🔍 [{agent_name}] 查询 '{query[:30]}...' 找到 {len(results)} 条")
        return results[:top_k]


    def get_agent_knowledge(self, agent_name: str) -> List[Dict]:
        """获取指定 Agent 的知识"""
        return self._agent_knowledge.get(agent_name, [])
    
    def get_stats(self) -> Dict:
        """获取联邦学习统计"""
        return {
            "total_knowledge": len(self._knowledge_base),
            "agents_count": len(self._agent_knowledge),
            "learning_rounds": self._learning_rounds,
            "agent_knowledge_counts": {
                agent: len(knowledge)
                for agent, knowledge in self._agent_knowledge.items()
            }
        }
    
    def _load_knowledge(self):
        """加载知识库"""
        knowledge_file = self.storage_dir / "knowledge_base.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r') as f:
                    data = json.load(f)
                    self._knowledge_base = data.get("knowledge_base", {})
                    self._agent_knowledge = defaultdict(list, data.get("agent_knowledge", {}))
            except Exception as e:
                print(f"加载知识库失败: {e}")
    
    def _save_knowledge(self):
        """保存知识库"""
        knowledge_file = self.storage_dir / "knowledge_base.json"
        try:
            with open(knowledge_file, 'w') as f:
                json.dump({
                    "knowledge_base": self._knowledge_base,
                    "agent_knowledge": dict(self._agent_knowledge),
                    "updated_at": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存知识库失败: {e}")


# 全局实例
federated_learning = FederatedLearning()
