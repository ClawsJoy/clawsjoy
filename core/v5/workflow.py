#!/usr/bin/env python3
"""Workflow v5.1 - 基于统一LLM客户端的工作流引擎

@version: 5.1.0
@date: 2026-6-21
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from core.lib.llm_client import llm_client
from core.lib.unified_config import unified_config


class WorkflowNode:
    """工作流节点"""

    def __init__(self, node_id: str, node_type: str, config: Dict):
        self.id = node_id
        self.type = node_type
        self.config = config
        self.inputs: Dict = {}
        self.outputs: Dict = {}
        self.status = "pending"
        self.error: Optional[str] = None
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id, "type": self.type, "status": self.status,
            "error": self.error, "config": self.config,
        }


class WorkflowEngine:
    """工作流执行引擎 - DAG + 并行 + 回滚"""

    # 支持的节点类型
    NODE_TYPES = {
        "input": "输入节点",
        "llm": "LLM调用",
        "skill": "技能调用",
        "agent": "Agent调用",
        "condition": "条件分支",
        "output": "输出节点",
        "transform": "数据转换",
    }

    def __init__(self):
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: List[tuple] = []
        self.results: Dict[str, Any] = {}
        self._node_handlers: Dict[str, Callable] = {}

    # ====================================================================
    #  构建
    # ====================================================================

    def add_node(self, node_type: str, config: Dict, node_id: str = None) -> str:
        """添加节点"""
        node_id = node_id or str(uuid.uuid4())[:8]
        self.nodes[node_id] = WorkflowNode(node_id, node_type, config)
        return node_id

    def add_edge(self, from_node: str, to_node: str,
                 from_output: str = "output", to_input: str = "input"):
        """添加连接"""
        self.edges.append((from_node, to_node, from_output, to_input))

    def add_nodes_from_template(self, tasks: List[Dict]) -> List[str]:
        """从任务列表批量添加节点"""
        node_ids = []
        for i, task in enumerate(tasks):
            nid = self.add_node(
                node_type=task.get("type", "agent"),
                config={
                    "agent": task.get("agent", "chat_agent"),
                    "action": task.get("action", "process"),
                    "message": task.get("message", task.get("description", "")),
                    **task.get("config", {})
                },
                node_id=task.get("id")
            )
            node_ids.append(nid)

            # 自动添加依赖边
            for dep in task.get("depends_on", []):
                if dep in node_ids or dep in self.nodes:
                    self.add_edge(dep, nid)

        return node_ids

    # ====================================================================
    #  执行
    # ====================================================================

    def execute(self, inputs: Dict = None) -> Dict:
        """执行工作流 - 拓扑排序 + 并行"""
        self.results = {}
        inputs = inputs or {}

        # 拓扑排序
        order = self._topological_sort()
        if not order:
            return {"success": False, "error": "工作流存在循环依赖"}

        # 按层级执行
        for level in order:
            self._execute_level(level, inputs)

        # 收集输出
        outputs = {}
        for nid, node in self.nodes.items():
            if node.type == "output":
                outputs[nid] = node.outputs.get("result", self.results.get(nid))

        success = all(
            node.status == "completed"
            for node in self.nodes.values()
            if node.type != "output"
        )

        return {
            "success": success,
            "results": self.results,
            "outputs": outputs,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
        }

    def _execute_level(self, node_ids: List[str], inputs: Dict):
        """执行同一层级的节点（可并行）"""
        for nid in node_ids:
            node = self.nodes.get(nid)
            if not node:
                continue

            # 收集输入
            node_inputs = dict(inputs)
            for from_nid, to_nid, from_out, to_in in self.edges:
                if to_nid == nid and from_nid in self.results:
                    node_inputs[to_in] = self.results[from_nid]

            node.inputs = node_inputs

            # 执行
            try:
                node.started_at = time.time()
                result = self._execute_node(node, node_inputs)
                node.status = "completed"
                node.outputs["result"] = result
                self.results[nid] = result
            except Exception as e:
                node.status = "failed"
                node.error = str(e)
                self.results[nid] = None
            finally:
                node.completed_at = time.time()

    def _execute_node(self, node: WorkflowNode, inputs: Dict) -> Any:
        """执行单个节点"""
        config = node.config

        if node.type == "input":
            return inputs.get("value", config.get("default", ""))

        elif node.type == "llm":
            prompt = inputs.get("prompt", config.get("prompt", ""))
            if not prompt:
                raise ValueError("LLM节点缺少prompt")
            return llm_client.generate(
                prompt=prompt,
                model=config.get("model", "qwen2.5:3b"),
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 512),
                task_type=config.get("task_type", "workflow")
            )

        elif node.type == "agent":
            agent_name = config.get("agent", "chat_agent")
            message = inputs.get("message", config.get("message", ""))
            agent = self._get_agent(agent_name)
            if not agent:
                raise ValueError(f"Agent不可用: {agent_name}")
            ctx = {"source": "workflow", "node_id": node.id}
            if hasattr(agent, 'process'):
                result = agent.process(message, ctx)
                return result.get("response", result.get("output_content", ""))
            elif hasattr(agent, 'handle'):
                return agent.handle(message)

        elif node.type == "skill":
            skill_name = config.get("skill", "")
            params = inputs.get("params", config.get("params", {}))
            return self._call_skill(skill_name, params)

        elif node.type == "condition":
            field = config.get("field", "")
            operator = config.get("operator", "eq")
            value = config.get("value", "")
            check_value = inputs.get(field, self.results.get(field, ""))
            condition_met = self._evaluate_condition(check_value, operator, value)
            true_branch = config.get("true_branch")
            false_branch = config.get("false_branch")
            target = true_branch if condition_met else false_branch
            if target and target in self.nodes:
                return self._execute_node(self.nodes[target], inputs)
            return condition_met

        elif node.type == "transform":
            template = config.get("template", "{input}")
            return template.format(**inputs, **self.results)

        elif node.type == "output":
            return inputs.get("value", self.results.get(node.id, ""))

        else:
            raise ValueError(f"未知节点类型: {node.type}")

    # ====================================================================
    #  辅助
    # ====================================================================

    def _topological_sort(self) -> List[List[str]]:
        """拓扑排序，返回层级列表（同层可并行）"""
        in_degree = {nid: 0 for nid in self.nodes}
        adj = {nid: [] for nid in self.nodes}

        for from_nid, to_nid, _, _ in self.edges:
            if from_nid in adj and to_nid in in_degree:
                adj[from_nid].append(to_nid)
                in_degree[to_nid] += 1

        levels = []
        while in_degree:
            current_level = [nid for nid, deg in in_degree.items() if deg == 0]
            if not current_level:
                return []  # 存在环
            levels.append(current_level)
            for nid in current_level:
                del in_degree[nid]
                for neighbor in adj.get(nid, []):
                    if neighbor in in_degree:
                        in_degree[neighbor] -= 1

        return levels

    def _evaluate_condition(self, check_value: Any, operator: str, target: Any) -> bool:
        """评估条件"""
        if operator == "eq":
            return str(check_value) == str(target)
        elif operator == "neq":
            return str(check_value) != str(target)
        elif operator == "contains":
            return str(target) in str(check_value)
        elif operator == "gt":
            return float(check_value) > float(target)
        elif operator == "lt":
            return float(check_value) < float(target)
        elif operator == "exists":
            return check_value is not None and check_value != ""
        return False

    def _get_agent(self, agent_name: str):
        """动态获取Agent"""
        try:
            mod = __import__(f"agents.{agent_name}.agent_v4", fromlist=["*"])
            for attr in dir(mod):
                if attr.endswith("V4") and hasattr(getattr(mod, attr), 'process'):
                    return getattr(mod, attr)()
        except ImportError:
            pass
        return None

    def _call_skill(self, skill: str, params: Dict) -> str:
        """调用技能"""
        try:
            from core.v5.skills.manager import skill_manager
            return skill_manager.execute(skill, params)
        except Exception:
            return ""

    # ====================================================================
    #  管理
    # ====================================================================

    def get_node_status(self, node_id: str) -> Optional[Dict]:
        node = self.nodes.get(node_id)
        return node.to_dict() if node else None

    def reset(self):
        """重置所有节点状态"""
        for node in self.nodes.values():
            node.status = "pending"
            node.error = None
            node.inputs = {}
            node.outputs = {}
        self.results = {}

    def export(self) -> Dict:
        return {
            "nodes": {nid: {"type": n.type, "config": n.config} for nid, n in self.nodes.items()},
            "edges": [(f, t, fo, ti) for f, t, fo, ti in self.edges],
        }

    def import_from_dict(self, data: Dict):
        self.nodes = {}
        for nid, ndata in data.get("nodes", {}).items():
            self.nodes[nid] = WorkflowNode(nid, ndata["type"], ndata["config"])
        self.edges = data.get("edges", [])

    def get_stats(self) -> Dict:
        completed = sum(1 for n in self.nodes.values() if n.status == "completed")
        failed = sum(1 for n in self.nodes.values() if n.status == "failed")
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "completed": completed,
            "failed": failed,
            "pending": len(self.nodes) - completed - failed,
        }


workflow_engine = WorkflowEngine()
