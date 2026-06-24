# core/orchestration/service.py
"""
编排服务 - 串联 TaskPlanner + TaskManager + 动态Agent发现

流程:
  TaskPlanner.plan()  →  模板匹配 + 意图识别
  TaskManager         →  状态机 + 回滚 + 持久化
  _get_agent()        →  三层降级动态发现
  ThreadPoolExecutor  →  并行执行
"""

import os
import sys
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeoutError
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.orchestration.planner import TaskPlanner
from engine.orchestration.task_manager import task_manager, TaskStatus

logger = logging.getLogger(__name__)


class OrchestrationService:
    """编排服务"""

    def __init__(self, max_workers: int = 8, task_timeout: int = 120):
        self.planner = TaskPlanner()
        self.task_manager = task_manager
        self.max_workers = max_workers
        self.task_timeout = task_timeout
        self._agent_cache: Dict[str, Any] = {}

    # ====================================================================
    #  主入口
    # ====================================================================

    def execute(self, user_input: str, user_id: str = "default") -> Dict:
        """执行编排"""
        try:
            # 1. 用 TaskPlanner 生成计划
            plan_data = self.planner.plan(user_input)
            if not plan_data.get("success"):
                return self._error_response("无法生成任务计划", plan_data)

            tasks_raw = plan_data.get("tasks", [])
            if not tasks_raw:
                return self._error_response("任务列表为空")

            # 2. 转为 TaskManager 格式
            formatted = self._format_tasks(tasks_raw, user_input)
            plan = self.task_manager.create_plan(
                name=plan_data.get("name", "编排任务"),
                description=plan_data.get("description", user_input[:100]),
                tasks=formatted
            )
            logger.info(f"[编排] 计划: {plan.id} | 意图: {plan_data.get('intent')} | {len(formatted)}个任务")

            # 3. 执行
            result = self._execute_plan(plan, user_id)

            # 4. 聚合
            return self._aggregate(plan, plan_data, result)

        except Exception as e:
            logger.error(f"[编排] 失败: {e}", exc_info=True)
            return self._error_response(f"编排执行失败: {str(e)}")

    # ====================================================================
    #  任务格式化
    # ====================================================================

    def _format_tasks(self, tasks: List[Dict], user_input: str) -> List[Dict]:
        """TaskPlanner 输出 → TaskManager 输入"""
        formatted = []
        for i, t in enumerate(tasks):
            formatted.append({
                "name": t.get("name", f"task_{i}"),
                "agent": t.get("agent", "chat_agent"),
                "action": t.get("action", "handle"),
                "params": {
                    "message": t.get("message", user_input),
                    "raw_input": user_input,
                },
                "depends_on": t.get("depends_on", []),
                "checkpoint": t.get("checkpoint", False),
                "optional": t.get("optional", False),
                "parallel_group": t.get("parallel_group"),
            })
        return formatted

    # ====================================================================
    #  执行引擎
    # ====================================================================

    def _execute_plan(self, plan, user_id: str) -> Dict:
        """执行计划"""
        plan.status = TaskStatus.RUNNING
        results: List[Dict] = []

        # 分组
        sequential = [t for t in plan.tasks if not t.parallel_group]
        parallel_groups = self._group_parallel(plan.tasks)

        # 串行
        for task in sequential:
            if task.status != TaskStatus.PENDING:
                continue
            result = self._run_task(task, user_id)
            results.append(result)
            if task.status == TaskStatus.FAILED and not task.optional:
                return self._finalize(plan, results, False)

        # 并行组
        for group_tasks in parallel_groups.values():
            group_results = self._run_parallel(group_tasks, user_id)
            results.extend(group_results)
            if any(not r.get("success") and not r.get("optional") for r in group_results):
                return self._finalize(plan, results, False)

        return self._finalize(plan, results, True)

    def _run_task(self, task, user_id: str) -> Dict:
        """执行单个任务"""
        task.status = TaskStatus.RUNNING

        agent = self._get_agent(task.agent, user_id)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = f"Agent '{task.agent}' 不可用"
            return self._result(task, False)

        try:
            message = task.params.get("message", task.params.get("raw_input", ""))
            context = {"session_id": task.params.get("session_id"), "task_id": task.id, "user_id": user_id}

            raw = None
            if hasattr(agent, 'process'):
                raw = agent.process(message, context)
            elif hasattr(agent, 'handle_json'):
                raw = agent.handle_json(message)
            elif hasattr(agent, 'handle'):
                raw = agent.handle(message)

            if raw is None:
                task.status = TaskStatus.FAILED
                task.error = "Agent 无可用方法"
                return self._result(task, False)

            task.status = TaskStatus.COMPLETED
            task.result = raw
            return self._result(task, True, raw)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return self._result(task, False, error=str(e))

    def _run_parallel(self, tasks, user_id: str) -> List[Dict]:
        """并行执行"""
        results = []
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(tasks))) as ex:
            futures = {ex.submit(self._run_task, t, user_id): t for t in tasks}
            for f in as_completed(futures):
                try:
                    results.append(f.result(timeout=self.task_timeout))
                except FutureTimeoutError:
                    t = futures[f]
                    t.status = TaskStatus.FAILED
                    t.error = "超时"
                    results.append(self._result(t, False, error="超时"))
                except Exception as e:
                    t = futures[f]
                    t.status = TaskStatus.FAILED
                    t.error = str(e)
                    results.append(self._result(t, False, error=str(e)))
        return results

    # ====================================================================
    #  Agent 发现（三层降级）
    # ====================================================================

    def _get_agent(self, agent_name: str, user_id: str):
        cache_key = f"{agent_name}:{user_id}"
        if cache_key in self._agent_cache:
            return self._agent_cache[cache_key]

        agent = (
            self._from_wisdom(agent_name, user_id)
            or self._from_registry(agent_name, user_id)
            or self._from_import(agent_name, user_id)
        )
        if agent:
            self._agent_cache[cache_key] = agent
        return agent

    def _from_wisdom(self, name: str, uid: str):
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            return wisdom_factory.get_wisdom_agent(name, uid)
        except Exception:
            return None

    def _from_registry(self, name: str, uid: str):
        try:
            from core.lib.agent_registry import agent_registry
            cls = agent_registry.get(name)
            return cls(uid) if cls else None
        except Exception:
            return None

    def _from_import(self, name: str, uid: str):
        try:
            import sys, os
            # 确保项目根目录在 path 中
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
        
            mod = __import__(f"agents.{name}.agent_v4", fromlist=["*"])
            for attr in dir(mod):
                if attr.endswith("V4") and hasattr(getattr(mod, attr), 'process'):
                    return getattr(mod, attr)(uid)
        except ImportError as e:
            pass
        return None

    # ====================================================================
    #  结果处理
    # ====================================================================

    def _result(self, task, success: bool, output: Dict = None, error: str = None) -> Dict:
        resp = ""
        if output:
            resp = output.get("response", output.get("output_content", ""))
        return {
            "task_id": task.id, "task_name": task.name, "agent": task.agent,
            "success": success, "response": resp[:500],
            "error": error or task.error, "optional": task.optional,
        }

    def _finalize(self, plan, results: List[Dict], success: bool):
        plan.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        done = sum(1 for r in results if r.get("success"))
        return {
            "success": success, "plan_id": plan.id, "results": results,
            "completed": done, "failed": len(results) - done,
            "summary": f"完成 {done}/{len(results)} 个任务",
        }

    def _aggregate(self, plan, plan_data: Dict, result: Dict) -> Dict:
        responses = [r.get("response", "") for r in result.get("results", []) if r.get("success") and r.get("response")]
        return {
            "success": result.get("success", False),
            "plan_id": plan.id,
            "intent": plan_data.get("intent"),
            "results": result.get("results", []),
            "response": "\n\n".join(responses) if responses else "任务完成",
            "summary": result.get("summary", ""),
            "total_estimated": plan_data.get("total_estimated", 0),
        }

    def _error_response(self, msg: str, extra: Dict = None) -> Dict:
        return {"success": False, "error": msg, "response": msg, "results": [], **(extra or {})}

    # ====================================================================
    #  查询接口
    # ====================================================================

    def get_status(self, plan_id: str) -> Dict:
        return self.task_manager.get_plan_status(plan_id)

    def list_plans(self) -> List[Dict]:
        return [
            {"id": pid, "name": p.name, "status": p.status.value}
            for pid, p in self.task_manager.active_plans.items()
        ]

    def clear_cache(self):
        self._agent_cache.clear()

    def _group_parallel(self, tasks) -> Dict[str, List]:
        groups: Dict[str, List] = {}
        for t in tasks:
            if t.parallel_group:
                groups.setdefault(t.parallel_group, []).append(t)
        return groups


# 全局单例
orchestration_service = OrchestrationService()


# ====================================================================
#  测试
# ====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("OrchestrationService 测试")
    print("=" * 60)

    tests = [
        "帮我制作一个关于AI的视频",
        "帮我写一段Python排序代码",
        "分析数据然后生成报告",
        "你好",
    ]

    for t in tests:
        result = orchestration_service.execute(t)
        print(f"\n📥 {t[:40]}")
        print(f"   成功: {result.get('success')}")
        print(f"   意图: {result.get('intent', 'N/A')}")
        print(f"   摘要: {result.get('summary', 'N/A')}")
        if result.get("response"):
            print(f"   响应: {result['response'][:200]}")
