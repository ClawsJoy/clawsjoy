#!/usr/bin/env python3
"""Graph - Graph 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime


class KnowledgeGraph:
    """知识图谱"""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.base_path = Path(f"{config_helper.get_data_root()}/v5/users/{user_id}/knowledge")
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.nodes: Dict[str, Dict] = {}
        self.edges: List[tuple] = []
        self._load()
    
    def _load(self):
        """加载数据"""
        nodes_file = self.base_path / "nodes.json"
        if nodes_file.exists():
            with open(nodes_file, 'r') as f:
                self.nodes = json.load(f)

        edges_file = self.base_path / "edges.json"
        if edges_file.exists():
            with open(edges_file, 'r') as f:
                self.edges = [tuple(e) for e in json.load(f)]
    
    def _save(self):
        """保存数据"""
        with open(self.base_path / "nodes.json", 'w') as f:
            json.dump(self.nodes, f, indent=2, ensure_ascii=False)

        with open(self.base_path / "edges.json", 'w') as f:
            json.dump(self.edges, f, indent=2)
    
    def add_node(self, node_id: str, name: str, node_type: str, properties: Dict = None):
        """添加节点"""
        self.nodes[node_id] = {
            "id": node_id,
            "name": name,
            "type": node_type,
            "properties": properties or {},
            "created_at": datetime.now().isoformat()
        }
        self._save()
    
    def add_relation(self, from_node: str, to_node: str, relation: str, weight: float = 1.0):
        """添加关系"""
        self.edges.append((from_node, to_node, relation, weight))
        self._save()
    
    def query_related(self, node_id: str, relation: str = None) -> List[Dict]:
        """查询相关节点"""
        results = []
        for f, t, r, w in self.edges:
            if f == node_id and (relation is None or r == relation):
                if t in self.nodes:
                    results.append({**self.nodes[t], "relation": r, "weight": w})
            if t == node_id and (relation is None or r == relation):
                if f in self.nodes:
                    results.append({**self.nodes[f], "relation": r, "weight": w})
        return sorted(results, key=lambda x: x.get("weight", 0), reverse=True)
    
    def infer(self, start_node: str, max_depth: int = 2) -> List[Dict]:
        """推理 - 广度优先遍历"""
        visited = set()
        results = []
        queue = [(start_node, 0)]

        while queue:
            node, depth = queue.pop(0)
            if node in visited or depth > max_depth:
                continue
            visited.add(node)

            if node != start_node and node in self.nodes:
                results.append(self.nodes[node])

            for f, t, r, w in self.edges:
                if f == node and t not in visited:
                    queue.append((t, depth + 1))
                if t == node and f not in visited:
                    queue.append((f, depth + 1))

        return results
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "types": list(set(n.get("type") for n in self.nodes.values()))
        }


knowledge_graph = KnowledgeGraph
