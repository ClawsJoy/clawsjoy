#!/usr/bin/env python3
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    name: str
    skill: str
    params: Dict = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Any = None

class WorkflowEngineV2:
    def __init__(self, workflow_id: str, tenant_id: str = "1"):
        self.workflow_id = workflow_id
        self.tenant_id = tenant_id
        self.steps: List[WorkflowStep] = []
        self.step_map = {}
        self.results = {}

    def add_step(self, name: str, skill: str, params: Dict = None,
                 depends_on: List[str] = None, **kwargs):
        step = WorkflowStep(
            name=name,
            skill=skill,
            params=params or {},
            depends_on=depends_on or []
        )
        self.steps.append(step)
        self.step_map[name] = step
        return self

    def _call_skill(self, step: WorkflowStep):
        """直接调用 Skill（不依赖 execute.py 动态加载）"""
        skill = step.skill
        params = step.params.copy()
        params["tenant_id"] = self.tenant_id

        if skill == "auth":
            resp = requests.get('http://localhost:8092/api/auth/health', timeout=5)
            return resp.json()
        elif skill == "tenant":
            resp = requests.get('http://localhost:8088/api/tenants', timeout=5)
            return resp.json()
        elif skill == "billing":
            tid = params.get("tenant_id", "1")
            resp = requests.get(f'http://localhost:8090/api/billing/balance?tenant_id={tid}', timeout=5)
            return resp.json()
        elif skill == "coffee":
            action = params.get("action")
            if action == "shops":
                resp = requests.get('http://localhost:8085/api/coffee/shops', timeout=5)
                return resp.json()
            elif action == "order":
                resp = requests.post('http://localhost:8085/api/coffee/order',
                                     json={"item": params.get("item", "拿铁"),
                                           "shop_id": params.get("shop_id", 1)},
                                     timeout=5)
                return resp.json()
        return {"error": f"Unknown skill: {skill}"}

    def execute(self) -> Dict:
        completed = set()
        max_iter = len(self.steps) * 2
        iter_count = 0

        while len(completed) < len(self.steps) and iter_count < max_iter:
            iter_count += 1
            for step in self.steps:
                if step.name in completed:
                    continue
                # 依赖未满足则跳过
                if step.depends_on and not all(d in completed for d in step.depends_on):
                    continue

                step.status = StepStatus.RUNNING
                print(f"▶️ 执行: {step.name} ({step.skill})")
                try:
                    result = self._call_skill(step)
                    step.result = result
                    step.status = StepStatus.COMPLETED
                    self.results[step.name] = {"success": True, "data": result}
                except Exception as e:
                    step.status = StepStatus.FAILED
                    self.results[step.name] = {"success": False, "error": str(e)}
                completed.add(step.name)

        return {
            "success": all(s.status == StepStatus.COMPLETED for s in self.steps),
            "workflow_id": self.workflow_id,
            "results": self.results,
            "steps": [{"name": s.name, "status": s.status.value} for s in self.steps]
        }

if __name__ == "__main__":
    engine = WorkflowEngineV2("fix_test", tenant_id="1")
    engine.add_step("auth", "auth", {})
    engine.add_step("balance", "billing", {"tenant_id": "1"})
    engine.add_step("shops", "coffee", {"action": "shops"})
    engine.add_step("order", "coffee", {"action": "order", "item": "拿铁", "shop_id": 1},
                    depends_on=["balance", "shops"])

    result = engine.execute()
    print(json.dumps(result, indent=2, ensure_ascii=False))
