#!/usr/bin/env python3
"""Workflow - Workflow 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
import time
import uuid
from typing import Dict, List, Any, Callable
from pathlib import Path
from core.lib.unified_config import unified_config


class WorkflowNode:
    """工作流节点"""
    def __init__(self, node_id: str, node_type: str, config: Dict):
        self.id = node_id
        self.type = node_type
        self.config = config
        self.inputs = {}
        self.outputs = {}
        self.status = "pending"


class WorkflowEngine:
    """工作流执行引擎"""
    
    def __init__(self):
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: List[tuple] = []
        self.results: Dict[str, Any] = {}
    
    def add_node(self, node_type: str, config: Dict) -> str:
        """添加节点"""
        node_id = str(uuid.uuid4())[:6]
        self.nodes[node_id] = WorkflowNode(node_id, node_type, config)
        return node_id
    
    def add_edge(self, from_node: str, to_node: str, from_output: str = "output"):
        """添加连接"""
        self.edges.append((from_node, to_node, from_output))
    
    def execute(self) -> Dict:
        """执行工作流"""
        # 按依赖排序
        executed = set()
        results = {}

        for node_id, node in self.nodes.items():
            if node_id in executed:
                continue
            result = self._execute_node(node_id, results)
            if result is not None:
                results[node_id] = result
                executed.add(node_id)

        return results
    
    def _execute_node(self, node_id: str, previous_results: Dict) -> Any:
        """执行单个节点"""
        node = self.nodes.get(node_id)
        if not node:
            return None

        # 获取输入
        inputs = {}
        for from_node, to_node, output in self.edges:
            if to_node == node_id and from_node in previous_results:
                inputs[output] = previous_results[from_node]

        # 执行节点逻辑
        if node.type == "input":
            result = inputs.get("value", node.config.get("value", ""))
        elif node.type == "llm":
            prompt = inputs.get("prompt", node.config.get("prompt", ""))
            result = self._call_llm(prompt)
        elif node.type == "skill":
            skill = node.config.get("skill", "")
            params = inputs.get("params", {})
            result = self._call_skill(skill, params)
        elif node.type == "output":
            result = inputs.get("value", previous_results.get(node_id, ""))
        else:
            result = None

        node.status = "completed"
        return result
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        import requests
        try:
            resp = requests.post(f"http://{unified_config.get("llm.endpoint", "http://localhost:11434")}/api/generate",
                json={"model": config_helper.get_llm_model(fast=True), "prompt": prompt, "stream": False}, timeout=config_helper.get_timeout("default"))
            return resp.json().get('response', '') if resp.status_code == 200 else ""
        except:
            return ""
    
    def _call_skill(self, skill: str, params: Dict) -> str:
        """调用技能"""
        from core.v5.skills.manager import skill_manager
        return skill_manager.execute(skill, params)
    
    def export(self) -> Dict:
        """导出工作流"""
        return {
            "nodes": {nid: {"type": n.type, "config": n.config} for nid, n in self.nodes.items()},
            "edges": self.edges
        }
    
    def import_from_dict(self, data: Dict):
        """导入工作流"""
        self.nodes = {}
        for nid, ndata in data.get('nodes', {}).items():
            self.nodes[nid] = WorkflowNode(nid, ndata['type'], ndata['config'])
        self.edges = data.get('edges', [])


workflow_engine = WorkflowEngine()
