#!/usr/bin/env python3
"""Skills Workflow 编排引擎"""

import json
import time
from typing import Dict, List, Any, Callable
from collections import defaultdict
from state_manager import SkillStateManager

class WorkflowStep:
    """工作流步骤"""
    def __init__(self, name: str, skill: str, params: Dict = None, depends_on: List[str] = None):
        self.name = name
        self.skill = skill
        self.params = params or {}
        self.depends_on = depends_on or []
        self.result = None
        self.status = "pending"  # pending, running, completed, failed

class WorkflowEngine:
    """工作流编排引擎"""
    
    def __init__(self, workflow_id: str, tenant_id: str = "1"):
        self.workflow_id = workflow_id
        self.tenant_id = tenant_id
        self.steps: List[WorkflowStep] = []
        self.state_manager = SkillStateManager()
    
    def add_step(self, name: str, skill: str, params: Dict = None, depends_on: List[str] = None) -> 'WorkflowEngine':
        """添加步骤"""
        self.steps.append(WorkflowStep(name, skill, params, depends_on))
        return self
    
    def _get_step_index(self, name: str) -> int:
        for i, step in enumerate(self.steps):
            if step.name == name:
                return i
        return -1
    
    def _check_dependencies(self, step: WorkflowStep, completed: set) -> bool:
        """检查依赖是否满足"""
        return all(dep in completed for dep in step.depends_on)
    
    def execute(self) -> Dict:
        """执行工作流（拓扑排序）"""
        completed = set()
        results = {}
        
        # 保存工作流状态
        self.state_manager.save_state(f"workflow:{self.workflow_id}", "state", {
            "steps": [{"name": s.name, "skill": s.skill, "status": "pending"} for s in self.steps]
        }, self.tenant_id)
        
        while len(completed) < len(self.steps):
            executed = False
            for step in self.steps:
                if step.name in completed or step.status == "failed":
                    continue
                
                if self._check_dependencies(step, completed):
                    step.status = "running"
                    
                    # 更新状态
                    self.state_manager.update_state(f"workflow:{self.workflow_id}", "state", {
                        f"step_{step.name}": "running"
                    }, self.tenant_id)
                    
                    # 执行步骤
                    try:
                        result = self._execute_skill(step.skill, step.params)
                        step.result = result
                        step.status = "completed"
                        completed.add(step.name)
                        results[step.name] = result
                        
                        # 更新状态
                        self.state_manager.update_state(f"workflow:{self.workflow_id}", "state", {
                            f"step_{step.name}": "completed",
                            f"result_{step.name}": json.dumps(result)[:500]
                        }, self.tenant_id)
                        executed = True
                        
                    except Exception as e:
                        step.status = "failed"
                        results[step.name] = {"error": str(e)}
                        self.state_manager.update_state(f"workflow:{self.workflow_id}", "state", {
                            f"step_{step.name}": "failed"
                        }, self.tenant_id)
                        return {"success": False, "results": results, "failed_at": step.name}
            
            if not executed:
                break
        
        all_completed = all(s.status == "completed" for s in self.steps)
        return {
            "success": all_completed,
            "results": results,
            "workflow_id": self.workflow_id
        }
    
    def _execute_skill(self, skill_name: str, params: Dict) -> Dict:
        """执行单个 Skill"""
        import importlib.util
        from pathlib import Path
        
        skill_path = Path(f"/home/flybo/clawsjoy/skills/{skill_name}/execute.py")
        if not skill_path.exists():
            return {"error": f"Skill '{skill_name}' not found"}
        
        spec = importlib.util.spec_from_file_location(f"{skill_name}_exec", skill_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        params["tenant_id"] = self.tenant_id
        return module.execute(params)

if __name__ == "__main__":
    print("✅ Workflow 编排引擎已加载")
    
    # 测试示例
    engine = WorkflowEngine("test_001")
    engine.add_step("health_check", "auth", {"action": "health"})
    engine.add_step("get_tenants", "tenant", {"action": "list"}, depends_on=["health_check"])
    
    result = engine.execute()
    print(json.dumps(result, indent=2, ensure_ascii=False))
