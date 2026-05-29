"""工作流引擎 - 可视化流程编排"""

from typing import Dict, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class WorkflowNode:
    """工作流节点"""
    id: str
    type: str  # input, llm, condition, output, tool
    name: str
    config: Dict = field(default_factory=dict)
    next_nodes: List[str] = field(default_factory=list)


@dataclass
class Workflow:
    """工作流定义"""
    id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class WorkflowEngine:
    """工作流执行引擎"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.results: Dict[str, Any] = {}
    
    def create_workflow(self, name: str, description: str, nodes: List[Dict]) -> str:
        """创建工作流"""
        workflow_id = str(uuid.uuid4())[:8]
        
        workflow_nodes = []
        for node in nodes:
            workflow_nodes.append(WorkflowNode(
                id=node.get('id', str(uuid.uuid4())[:8]),
                type=node.get('type', 'llm'),
                name=node.get('name', ''),
                config=node.get('config', {}),
                next_nodes=node.get('next_nodes', [])
            ))
        
        self.workflows[workflow_id] = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            nodes=workflow_nodes
        )
        
        return workflow_id
    
    def execute(self, workflow_id: str, input_data: str) -> Dict:
        """执行工作流"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"success": False, "error": "Workflow not found"}
        
        context = {"input": input_data, "output": ""}
        
        # 找到起始节点
        start_node = next((n for n in workflow.nodes if n.type == "input"), workflow.nodes[0])
        
        current_node = start_node
        visited = set()
        
        while current_node and current_node.id not in visited:
            visited.add(current_node.id)
            
            # 执行节点
            result = self._execute_node(current_node, context)
            context["output"] = result
            
            # 找下一个节点
            if current_node.next_nodes:
                next_id = current_node.next_nodes[0]
                current_node = next((n for n in workflow.nodes if n.id == next_id), None)
            else:
                break
        
        return {"success": True, "result": context["output"]}
    
    def _execute_node(self, node: WorkflowNode, context: Dict) -> str:
        """执行单个节点"""
        from core.v5.llm.client import llm
        
        if node.type == "input":
            return context.get("input", "")
        
        elif node.type == "llm":
            prompt = node.config.get("prompt", "请处理: {input}").format(**context)
            return llm.generate(prompt)
        
        elif node.type == "output":
            return context.get("output", "")
        
        return ""


workflow_engine = WorkflowEngine()
