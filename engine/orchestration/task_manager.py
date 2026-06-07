"""任务编排引擎 - 支持状态管理和回滚"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"
    ROLLED_BACK = "rolled_back"


@dataclass
class SubTask:
    id: str
    name: str
    agent: str
    action: str
    params: Dict
    depends_on: List[str] = field(default_factory=list)
    rollback_action: Optional[str] = None
    rollback_params: Optional[Dict] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    checkpoint: bool = False
    optional: bool = False
    parallel_group: Optional[str] = None
    interactive: bool = False


@dataclass
class OrchestrationPlan:
    id: str
    name: str
    description: str
    tasks: List[SubTask]
    created_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    current_task: Optional[str] = None
    checkpoints: Dict[str, Any] = field(default_factory=dict)


class TaskManager:
    def __init__(self, storage_dir: str = "data/orchestration"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.active_plans: Dict[str, OrchestrationPlan] = {}

    def create_plan(
        self, name: str, description: str, tasks: List[Dict]
    ) -> OrchestrationPlan:
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        subtasks = []
        for i, task in enumerate(tasks):
            subtasks.append(
                SubTask(
                    id=f"{plan_id}_{i}",
                    name=task.get("name"),
                    agent=task.get("agent"),
                    action=task.get("action", "handle"),
                    params=task.get("params", {}),
                    depends_on=task.get("depends_on", []),
                    rollback_action=task.get("rollback_action"),
                    rollback_params=task.get("rollback_params", {}),
                    checkpoint=task.get("checkpoint", False),
                    optional=task.get("optional", False),
                    parallel_group=task.get("parallel_group"),
                    interactive=task.get("interactive", False),
                )
            )

        plan = OrchestrationPlan(
            id=plan_id, name=name, description=description, tasks=subtasks
        )

        self.active_plans[plan_id] = plan
        self._save_plan(plan)
        return plan

    def execute_plan_parallel(self, plan_id: str, agent_getter) -> Dict:
        plan = self.active_plans.get(plan_id)
        if not plan:
            return {"success": False, "error": "计划不存在"}

        plan.status = TaskStatus.RUNNING
        completed_ids = set()
        results = []

        for task in plan.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            agent = agent_getter(task.agent)
            if not agent:
                task.status = TaskStatus.FAILED
                task.error = f"Agent {task.agent} 不可用"
                results.append(
                    {"task": task.name, "success": False, "error": task.error}
                )
                if not task.optional:
                    return self._format_result(plan, results, False)
                continue

            result = self._execute_task(agent, task)
            task.status = result.status
            task.result = result.result
            task.error = result.error
            results.append(
                {
                    "task": task.name,
                    "success": task.status == TaskStatus.COMPLETED,
                    "response": (
                        task.result.get("response", "")[:200]
                        if task.result
                        else task.error
                    ),
                }
            )

            if task.status == TaskStatus.COMPLETED:
                completed_ids.add(task.id)
            elif not task.optional:
                return self._format_result(plan, results, False)

        plan.status = TaskStatus.COMPLETED
        return self._format_result(plan, results, True)

    def _execute_task(self, agent, task: SubTask) -> SubTask:
        if not hasattr(agent, "handle"):
            task.status = TaskStatus.FAILED
            task.error = f"Agent {task.agent} 没有 handle 方法"
            return task

        method = getattr(agent, "handle")
        message = task.params.get("message", "")

        try:
            result = method(message, None)
            task.status = TaskStatus.COMPLETED
            task.result = result
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)

        return task

    def _format_result(
        self, plan: OrchestrationPlan, results: List, success: bool
    ) -> Dict:
        return {
            "success": success,
            "plan_id": plan.id,
            "total_tasks": len(plan.tasks),
            "completed": len(
                [t for t in plan.tasks if t.status == TaskStatus.COMPLETED]
            ),
            "failed": len([t for t in plan.tasks if t.status == TaskStatus.FAILED]),
            "results": results,
        }

    def _save_plan(self, plan: OrchestrationPlan):
        import json

        plan_data = {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "created_at": plan.created_at.isoformat(),
            "status": plan.status.value,
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "agent": t.agent,
                    "status": t.status.value,
                    "result": t.result,
                    "error": t.error,
                }
                for t in plan.tasks
            ],
        }
        with open(self.storage_dir / f"{plan.id}.json", "w") as f:
            json.dump(plan_data, f, indent=2, ensure_ascii=False)

    def get_plan_status(self, plan_id: str) -> Dict:
        plan = self.active_plans.get(plan_id)
        if not plan:
            return {"success": False, "error": "计划不存在"}

        return {
            "success": True,
            "plan_id": plan.id,
            "name": plan.name,
            "status": plan.status.value,
            "progress": f"{len([t for t in plan.tasks if t.status == TaskStatus.COMPLETED])}/{len(plan.tasks)}",
            "tasks": [
                {"name": t.name, "status": t.status.value, "error": t.error}
                for t in plan.tasks
            ],
        }


task_manager = TaskManager()
