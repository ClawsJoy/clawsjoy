"""用户友好的编排器 - 对话式任务管理"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from core.orchestration.planner import ProgressTracker, TaskExecutor, TaskPlanner


class UserOrchestrator:
    """用户友好的编排器"""

    def __init__(self):
        self.planner = TaskPlanner()
        self.executor = TaskExecutor()
        self.tracker = ProgressTracker()
        self.active_plans = {}

    def start(self, user_input: str, user_id: str) -> Dict:
        print(f"[DEBUG start] user_id={user_id}, input={user_input}")
        """开始一个任务"""

        # 1. 生成计划
        plan = self.planner.plan(user_input)
        print(f"[DEBUG start] plan={plan}")
        if not plan.get("success"):
            return {"success": False, "message": "无法理解您的需求"}

        plan_id = str(uuid.uuid4())[:8]

        # 2. 展示计划给用户
        tasks = plan.get("tasks", [])
        total_time = plan.get("total_estimated", 0)

        response = f"""📋 收到您的需求：「{user_input}」

        我将按照以下计划执行:
        """
        for i, task in enumerate(tasks, 1):
            optional_tag = " [可选]" if task.get("optional") else ""
            time_tag = f" ({task.get('estimated', 0)}秒)"
            response += f"{i}. {task.get('message')}{optional_tag}{time_tag}\n"

        response += f"\n⏱️ 预估总时间: {total_time}秒"
        response += "\n\n是否开始执行？(回复「开始」继续，或「修改」调整计划)"

        # 保存计划
        self.active_plans[plan_id] = {
            "plan": plan,
            "user_id": user_id,
            "status": "waiting_confirmation",
            "current_index": 0,
            "results": [],
            "created_at": datetime.now().isoformat(),
        }
        print(f"[DEBUG start] 已保存计划: plan_id={plan_id}, user_id={user_id}")

        return {"success": True, "plan_id": plan_id, "message": response, "plan": plan}

    def confirm(self, plan_id: str, user_input: str) -> Dict:
        """确认并开始执行"""
        plan_data = self.active_plans.get(plan_id)
        if not plan_data:
            return {"success": False, "message": "计划不存在"}

        if "开始" in user_input:
            return self._execute_plan(plan_id)
        elif "修改" in user_input:
            return self._modify_plan(plan_id, user_input)
        elif "暂停" in user_input:
            return self._pause_plan(plan_id)
        elif "继续" in user_input:
            return self._resume_plan(plan_id)
        elif "取消" in user_input:
            return self._cancel_plan(plan_id)
        else:
            return {
                "success": False,
                "message": "请回复「开始」、「修改」、「暂停」或「取消」",
            }

    def _execute_plan(self, plan_id: str) -> Dict:
        """执行计划"""
        plan_data = self.active_plans.get(plan_id)
        plan = plan_data["plan"]
        tasks = plan.get("tasks", [])
        user_id = plan_data["user_id"]

        start_index = plan_data.get("current_index", 0)
        results = plan_data.get("results", [])

        for i in range(start_index, len(tasks)):
            task = tasks[i]

            # 通知开始
            self._notify(f"\n🔄 执行中: {task.get('message')}...")

            # 执行任务
            result = self.executor.execute(task, user_id)
            results.append(result)

            # 保存进度
            plan_data["current_index"] = i + 1
            plan_data["results"] = results
            self.tracker.save(plan_id, plan_data)

            # 显示结果
            if result.get("success"):
                self._notify(f"✅ {task.get('message')} 完成")
            else:
                self._notify(
                    f"❌ {task.get('message')} 失败: {result.get('result', {}).get('error', '未知错误')}"
                )

                # 询问处理方式
                return {
                    "success": False,
                    "plan_id": plan_id,
                    "message": f"任务「{task.get('message')}」失败，是否重试、跳过或回滚？",
                    "failed_task": task.get("name"),
                }

            # 显示进度
            progress = self.tracker.format_progress(i + 1, len(tasks))
            self._notify(f"进度: {progress}")

        # 全部完成
        plan_data["status"] = "completed"
        self.tracker.save(plan_id, plan_data)

        return {
            "success": True,
            "plan_id": plan_id,
            "message": "🎉 所有任务已完成！",
            "results": results,
        }

    def _notify(self, message: str):
        """通知用户（通过 print，实际应通过 WebSocket）"""
        print(message)

    def get_status(self, plan_id: str) -> Dict:
        """获取计划状态"""
        plan_data = self.tracker.load(plan_id)
        if not plan_data:
            return {"success": False, "message": "计划不存在"}

        plan = plan_data.get("plan", {})
        tasks = plan.get("tasks", [])
        results = plan_data.get("results", [])

        return {
            "success": True,
            "status": plan_data.get("status", "unknown"),
            "progress": f"{len(results)}/{len(tasks)}",
            "completed_tasks": [r.get("task") for r in results if r.get("success")],
            "current_task": (
                tasks[plan_data.get("current_index", 0)].get("message")
                if plan_data.get("current_index") < len(tasks)
                else None
            ),
        }

    def _execute_plan(self, plan_id: str) -> Dict:
        """执行计划"""
        plan_data = self.active_plans.get(plan_id)
        plan = plan_data["plan"]
        tasks = plan.get("tasks", [])
        user_id = plan_data["user_id"]

        print(f"[DEBUG] 开始执行计划，共 {len(tasks)} 个任务")

        for i, task in enumerate(tasks):
            print(f"[DEBUG] 执行任务 {i+1}/{len(tasks)}: {task.get('name')}")

            # 通知开始
            self._notify(f"\n🔄 执行中: {task.get('message')}...")

            # 执行任务
            result = self.executor.execute(task, user_id)
            print(f"[DEBUG] 任务结果: {result}")

            if not result.get("success"):
                return {
                    "success": False,
                    "message": f"任务执行失败: {result.get('error', '未知错误')}",
                    "failed_task": task.get("name"),
                }

        return {"success": True, "message": "任务执行完成", "results": results}

    def get_pending_plan_by_user(self, user_id: str) -> Optional[Dict]:
        print(
            f"[DEBUG get_pending] user_id={user_id}, active_plans={self.active_plans}"
        )
        """根据 user_id 获取等待确认的计划"""
        for plan_id, plan_data in self.active_plans.items():
            if (
                plan_data.get("user_id") == user_id
                and plan_data.get("status") == "waiting_confirmation"
            ):
                return {
                    "plan_id": plan_id,
                    "plan": plan_data.get("plan"),
                    "status": plan_data.get("status"),
                    "created_at": plan_data.get("created_at"),
                }
        return None

    def get_all_plans_by_user(self, user_id: str) -> List[Dict]:
        """获取用户的所有计划"""
        plans = []
        for plan_id, plan_data in self.active_plans.items():
            if plan_data.get("user_id") == user_id:
                plans.append(
                    {
                        "plan_id": plan_id,
                        "status": plan_data.get("status"),
                        "created_at": plan_data.get("created_at"),
                    }
                )
        return plans

    def confirm_by_user(self, user_input: str, user_id: str) -> Dict:
        """根据 user_id 自动关联并确认计划"""
        # 查找用户等待确认的计划
        pending = self.get_pending_plan_by_user(user_id)

        if not pending:
            return {"success": False, "message": "没有等待确认的计划"}

        plan_id = pending["plan_id"]
        return self.confirm(plan_id, user_input)


# 全局实例
user_orchestrator = UserOrchestrator()
