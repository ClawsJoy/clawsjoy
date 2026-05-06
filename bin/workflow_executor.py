#!/usr/bin/env python3
"""工作流执行器 - 修复版"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class WorkflowExecutor:
    def __init__(self):
        self.workflows_dir = Path("/mnt/d/clawsjoy/workflows")
        self.skills_dir = Path("/mnt/d/clawsjoy/skills")
        self.logs_dir = Path("/mnt/d/clawsjoy/logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def load_workflow(self, name):
        wf_file = self.workflows_dir / f"{name}.json"
        if not wf_file.exists():
            return None
        with open(wf_file, 'r') as f:
            return json.load(f)
    
    def execute_skill(self, skill_name, params, context):
        skill_file = self.skills_dir / f"{skill_name}.py"
        if not skill_file.exists():
            skill_file = Path("/mnt/d/clawsjoy/bin") / f"{skill_name}.py"
        
        if not skill_file.exists():
            return {"success": False, "error": f"Skill {skill_name} not found"}
        
        try:
            # 传递完整上下文
            params['_context'] = context
            input_json = json.dumps(params, ensure_ascii=False)
            cmd = [sys.executable, str(skill_file)]
            result = subprocess.run(cmd, input=input_json, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and result.stdout:
                output = json.loads(result.stdout)
                return {"success": True, "output": output}
            else:
                return {"success": False, "error": result.stderr or "无输出"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run(self, workflow_name, inputs=None):
        workflow = self.load_workflow(workflow_name)
        if not workflow:
            return {"success": False, "error": f"Workflow {workflow_name} not found"}
        
        print(f"🚀 执行工作流: {workflow_name}")
        
        context = inputs or {}
        step_results = {}
        steps = workflow.get("steps", [])
        
        for step in steps:
            step_name = step.get("name", step.get("skill"))
            skill_name = step.get("skill")
            params = step.get("params", {}).copy()
            
            # 添加步骤结果到上下文
            params['_step_results'] = step_results
            params['_context'] = context
            
            print(f"  📌 执行: {step_name}")
            result = self.execute_skill(skill_name, params, context)
            
            step_results[step_name] = result
            if result.get("success"):
                output = result.get("output", {})
                context[step_name] = output
                # 同时也将输出合并到顶层上下文
                if isinstance(output, dict):
                    for k, v in output.items():
                        if k not in ['success']:
                            context[k] = v
                print(f"     ✅ 成功")
            else:
                print(f"     ❌ 失败: {result.get('error')}")
                break
        
        success_count = sum(1 for r in step_results.values() if r.get("success"))
        
        return {
            "success": success_count == len(steps),
            "workflow": workflow_name,
            "total_steps": len(steps),
            "success_steps": success_count,
            "results": step_results,
            "context": {k: v for k, v in context.items() if not callable(v)}
        }

if __name__ == "__main__":
    executor = WorkflowExecutor()
    if len(sys.argv) > 1:
        result = executor.run(sys.argv[1])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("可用工作流:", executor.list_workflows())
