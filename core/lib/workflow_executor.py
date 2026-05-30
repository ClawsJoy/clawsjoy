from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""
Agent 工作流执行器
负责执行多 Agent 协作工作流
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from core.lib.agent_bus import get_bus


class WorkflowExecutor:
    """工作流执行器"""
    
    def __init__(self):
        self.workflows = self._load_workflows()
        self.bus = get_bus()
        self.running_workflows = {}

    def _load_workflows(self) -> Dict:
        """加载工作流配置"""
        config_file = Path("config/agent_workflows.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = unified_config.get("workflow_executor", {})
                return data.get('workflows', {})
        return {}
    
    def get_workflow(self, name: str) -> Dict:
        """获取工作流定义"""
        return self.workflows.get(name)
    
    def get_workflow_by_keyword(self, text: str) -> str:
        """根据关键词匹配工作流"""
        config_file = Path("config/agent_workflows.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = unified_config.get("workflow_executor", {})
                triggers = data.get('triggers', [])
                
                for trigger in triggers:
                    for keyword in trigger.get('keyword', []):
                        if keyword in text:
                            return trigger.get('workflow')
        return None
    
    def execute_workflow(self, workflow_name: str, input_data: Dict) -> Dict:
        """执行工作流"""
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            return {"success": False, "error": f"工作流不存在: {workflow_name}"}

        workflow_id = f"{workflow_name}_{datetime.now().timestamp()}"

        print(f"\n🚀 开始执行工作流: {workflow['name']}")
        print(f"   ID: {workflow_id}")

        results = {}
        current_data = input_data

        for step in workflow.get('steps', []):
            step_num = step.get('step')
            agent = step.get('agent')
            action = step.get('action')

            print(f"\n📌 步骤 {step_num}: {agent} -> {action}")

            # 发送消息到 Agent
            message_id = self.bus.publish(
                "workflow_executor",
                f"task.{action}",
                {
                    "action": action,
                    "params": current_data,
                    "workflow_id": workflow_id,
                    "step": step_num
                }
            )

            results[f"step_{step_num}"] = {
                "agent": agent,
                "action": action,
                "message_id": message_id,
                "status": "sent"
            }

            # 更新数据供下一步使用
            current_data = {"previous_result": results}

        self.running_workflows[workflow_id] = {
            "name": workflow_name,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "results": results
        }

        return {
            "success": True,
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "message": f"工作流已启动，共 {len(workflow.get('steps', []))} 个步骤"
        }
    
    def get_status(self, workflow_id: str = None) -> Dict:
        """获取工作流状态"""
        if workflow_id:
            return self.running_workflows.get(workflow_id, {"status": "not_found"})
        return {
            "running": len(self.running_workflows),
            "workflows": list(self.running_workflows.keys())
        }


# 全局实例
_workflow_executor = None

def get_workflow_executor() -> WorkflowExecutor:
    global _workflow_executor
    if _workflow_executor is None:
        _workflow_executor = WorkflowExecutor()
    return _workflow_executor
