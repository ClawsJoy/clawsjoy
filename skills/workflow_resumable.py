#!/usr/bin/env python3
"""Workflow 引擎 - 支持暂停/恢复"""

import json
import time
import pickle
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

STATE_DIR = Path("/home/flybo/clawsjoy/data/workflow_states")
STATE_DIR.mkdir(parents=True, exist_ok=True)

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class ResumableWorkflow:
    """可暂停/恢复的 Workflow"""
    
    def __init__(self, workflow_id: str, tenant_id: str = "1"):
        self.workflow_id = workflow_id
        self.tenant_id = tenant_id
        self.steps = []
        self.results = {}
        self.current_step_index = 0
        self.status = "pending"  # pending, running, paused, completed, failed
        self.state_file = STATE_DIR / f"{tenant_id}_{workflow_id}.pkl"
    
    def add_step(self, name: str, skill: str, params: Dict = None, depends_on: List[str] = None):
        """添加步骤"""
        self.steps.append({
            "name": name,
            "skill": skill,
            "params": params or {},
            "depends_on": depends_on or [],
            "status": StepStatus.PENDING.value,
            "result": None
        })
        return self
    
    def save_state(self):
        """保存状态"""
        state = {
            "workflow_id": self.workflow_id,
            "tenant_id": self.tenant_id,
            "steps": self.steps,
            "results": self.results,
            "current_step_index": self.current_step_index,
            "status": self.status,
            "updated_at": datetime.now().isoformat()
            "created_at": state.get("created_at", datetime.now().isoformat()),
        }
        with open(self.state_file, 'wb') as f:
            pickle.dump(state, f)
        print(f"💾 状态已保存: {self.state_file}")
    
    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, 'rb') as f:
                state = pickle.load(f)
            self.steps = state["steps"]
            self.results = state["results"]
            self.current_step_index = state["current_step_index"]
            self.status = state["status"]
            print(f"📂 状态已加载: {self.state_file}")
            return True
        return False
    
    def pause(self):
        """暂停 Workflow"""
        self.status = "paused"
        self.save_state()
        print(f"⏸️ Workflow {self.workflow_id} 已暂停")
    
    def resume(self):
        """恢复 Workflow"""
        if self.load_state():
            self.status = "running"
            self.execute()
        else:
            print(f"❌ 找不到 Workflow {self.workflow_id} 的状态")
    
    def _call_skill(self, skill_name: str, params: Dict) -> Dict:
        """调用 Skill"""
        import importlib.util
        skill_path = Path(f"/home/flybo/clawsjoy/skills/{skill_name}/execute.py")
        if not skill_path.exists():
            return {"error": f"Skill '{skill_name}' not found"}
        
        spec = importlib.util.spec_from_file_location(f"{skill_name}_exec", skill_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.execute(params)
    
    def execute(self):
        """执行 Workflow"""
        self.status = "running"
        completed = set()
        
        for step in self.steps[self.current_step_index:]:
            if step["status"] == StepStatus.COMPLETED.value:
                completed.add(step["name"])
                continue
            
            # 检查依赖
            if step["depends_on"] and not all(d in completed for d in step["depends_on"]):
                continue
            
            step["status"] = StepStatus.RUNNING.value
            self.save_state()
            
            print(f"▶️ 执行: {step['name']} ({step['skill']})")
            
            try:
                result = self._call_skill(step["skill"], step["params"])
                step["result"] = result
                step["status"] = StepStatus.COMPLETED.value
                self.results[step["name"]] = result
                completed.add(step["name"])
                self.current_step_index += 1
                self.save_state()
                
            except Exception as e:
                step["status"] = StepStatus.FAILED.value
                step["result"] = {"error": str(e)}
                self.status = "failed"
                self.save_state()
                print(f"❌ 步骤失败: {step['name']}")
                return {"success": False, "failed_at": step["name"]}
        
        self.status = "completed"
        self.save_state()
        return {"success": True, "results": self.results}
    
    def get_progress(self) -> Dict:
        """获取进度"""
        completed = sum(1 for s in self.steps if s["status"] == StepStatus.COMPLETED.value)
        total = len(self.steps)
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "progress": f"{completed}/{total}",
            "percent": int(completed / total * 100) if total > 0 else 0,
            "steps": self.steps
        }

if __name__ == "__main__":
    # 测试
    wf = ResumableWorkflow("test_resume")
    wf.add_step("auth", "auth", {"action": "health"})
    wf.add_step("balance", "billing", {"action": "balance", "tenant_id": "1"}, depends_on=["auth"])
    
    print("=== 执行 Workflow ===")
    result = wf.execute()
    print(f"结果: {result}")
    
    print(f"\n=== 进度 ===")
    print(json.dumps(wf.get_progress(), indent=2))
    
    # 测试暂停/恢复
    wf2 = ResumableWorkflow("test_pause")
    wf2.add_step("auth", "auth", {"action": "health"})
    wf2.add_step("shops", "coffee", {"action": "shops"}, depends_on=["auth"])
    
    print("\n=== 执行到一半暂停 ===")
    # 模拟执行一部分后暂停
    print("执行: auth")
    print("⏸️ 手动暂停...")
    wf2.pause()
    
    print("\n=== 恢复执行 ===")
    wf2.resume()

# 添加 Webhook 通知支持
import sys
sys.path.insert(0, '/home/flybo/clawsjoy/bin')
try:
    # from webhook_notify import get_notify
    HAS_WEBHOOK = False
except ImportError:
    HAS_WEBHOOK = False
    print("⚠️ Webhook 模块未加载")

# 在 execute 方法末尾添加通知
# 在完成或失败时调用
