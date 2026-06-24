# engine/orchestration/user_friendly.py
"""用户友好的任务编排 - 对话式、可中断、可恢复、实时进度"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional

from engine.orchestration.task_manager import TaskManager, TaskStatus
from core.orchestration.planner import TaskPlanner, TaskExecutor


class UserChoice(Enum):
    CONTINUE = "continue"
    RETRY = "retry"
    SKIP = "skip"
    ADJUST = "adjust"
    ROLLBACK = "rollback"
    PAUSE = "pause"
    RESUME = "resume"


@dataclass
class UserFriendlyTask:
    """用户友好的任务定义"""
    name: str
    description: str
    agent: str
    action: str
    params: Dict
    estimated_time: int = 10
    can_skip: bool = False
    can_retry: bool = True
    requires_confirmation: bool = False
    on_start: Optional[str] = None
    on_complete: Optional[str] = None
    on_error: Optional[str] = None
    confirm_message: Optional[str] = None


class UserFriendlyOrchestrator:
    """用户友好的编排器 - 实时反馈 + 人机协作"""

    def __init__(self, user_id: str = "default",
                 user_callback: Optional[Callable] = None):
        self.user_id = user_id
        self.user_callback = user_callback or self._default_callback
        self.planner = TaskPlanner()
        self.executor = TaskExecutor()
        self.task_manager = TaskManager()
        self.current_plan_id: Optional[str] = None
        self.paused = False
        self.interrupted = False

    # ====================================================================
    #  视频制作模板（保留兼容）
    # ====================================================================

    def create_video_plan(self, topic: str) -> List[UserFriendlyTask]:
        """创建视频制作计划"""
        return [
            UserFriendlyTask(
                name="understand",
                description=f"理解需求：制作关于「{topic}」的视频",
                agent="chat_agent", action="understand",
                params={"topic": topic},
                estimated_time=5,
                on_start="🤔 让我理解一下你的需求...",
            ),
            UserFriendlyTask(
                name="collect",
                description="📦 收集素材（图片、视频片段）",
                agent="video_agent", action="search",
                params={"keyword": topic},
                estimated_time=30,
                on_start="🔍 正在搜索相关素材...",
                on_complete="✅ 素材收集完成",
                on_error="⚠️ 素材收集失败，是否重试？",
            ),
            UserFriendlyTask(
                name="script",
                description="✍️ 生成视频脚本",
                agent="writer_agent", action="write",
                params={"topic": topic},
                estimated_time=20,
                on_start="📝 正在撰写脚本...",
                on_complete="✅ 脚本生成完成",
            ),
            UserFriendlyTask(
                name="voice",
                description="🎤 制作配音",
                agent="audio_agent", action="tts",
                params={},
                estimated_time=15, can_skip=True,
                requires_confirmation=True,
                confirm_message="是否需要配音？",
                on_start="🔊 正在生成配音...",
                on_complete="✅ 配音完成",
            ),
            UserFriendlyTask(
                name="edit",
                description="✂️ 剪辑视频",
                agent="video_agent", action="edit",
                params={},
                estimated_time=60,
                on_start="🎬 正在剪辑视频，请稍候...",
                on_complete="✅ 视频剪辑完成",
            ),
            UserFriendlyTask(
                name="subtitle",
                description="📝 添加字幕",
                agent="video_agent", action="subtitle",
                params={},
                estimated_time=10, can_skip=True,
                requires_confirmation=True,
                confirm_message="是否需要添加字幕？",
                on_start="📝 正在生成字幕...",
                on_complete="✅ 字幕已添加",
            ),
        ]

    # ====================================================================
    #  智能编排入口
    # ====================================================================

    def execute(self, user_input: str) -> Dict:
        """智能执行：自动识别意图并编排"""
        # 1. 用 TaskPlanner 生成计划
        plan_data = self.planner.plan(user_input)

        tasks = plan_data.get("tasks", [])
        if not tasks:
            return {"success": False, "response": "无法理解该任务"}

        # 2. 创建计划
        formatted = []
        for t in tasks:
            formatted.append({
                "name": t.get("name"),
                "agent": t.get("agent"),
                "action": t.get("action", "handle"),
                "params": {"message": t.get("message", user_input)},
                "depends_on": t.get("depends_on", []),
                "optional": t.get("optional", False),
            })

        plan = self.task_manager.create_plan(
            name=plan_data.get("name", "任务"),
            description=plan_data.get("description", user_input[:100]),
            tasks=formatted
        )
        self.current_plan_id = plan.id

        # 3. 展示计划
        self._notify(f"📋 {plan.name}")
        self._notify(f"   {plan.description}")
        self._notify(f"   共 {len(tasks)} 个任务，预计 {plan_data.get('total_estimated', 0)} 秒\n")

        # 4. 执行
        result = self.task_manager.execute_plan(
            plan.id,
            lambda name: self.executor._get_agent(name, self.user_id)
        )

        # 5. 聚合
        responses = [
            r.get("response", "")
            for r in result.get("results", [])
            if r.get("success") and r.get("response")
        ]

        return {
            "success": result.get("success", False),
            "plan_id": plan.id,
            "intent": plan_data.get("intent"),
            "response": "\n\n".join(responses) if responses else "任务完成",
            "summary": result.get("summary", ""),
            "results": result.get("results", []),
        }

    # ====================================================================
    #  带反馈的执行
    # ====================================================================

    def execute_with_feedback(self, tasks: List[UserFriendlyTask]) -> Dict:
        """逐任务执行，实时反馈 + 用户干预"""
        results = []

        for i, task in enumerate(tasks):
            if self.interrupted:
                return {"success": False, "reason": "用户中断"}

            # 开始通知
            self._notify(task.on_start or f"▶️ 开始: {task.description}")

            # 确认
            if task.requires_confirmation:
                choice = self._ask_user(
                    task.confirm_message or f"是否执行「{task.description}」？",
                    options=["继续", "跳过"]
                )
                if choice == UserChoice.SKIP:
                    self._notify(f"⏭️ 已跳过: {task.name}")
                    continue
                elif choice == UserChoice.ROLLBACK:
                    self._rollback(results)
                    return {"success": False, "reason": "用户取消"}

            # 执行
            try:
                raw_task = {
                    "name": task.name, "agent": task.agent,
                    "action": task.action, "message": task.description,
                }
                result = self.executor.execute(raw_task, self.user_id)
                results.append(result)

                if result.get("success"):
                    self._notify(task.on_complete or f"✅ {task.name} 完成")
                else:
                    self._notify(task.on_error or f"❌ {task.name} 失败: {result.get('error')}")
                    if task.can_retry:
                        choice = self._ask_user("是否重试？", ["重试", "跳过", "停止"])
                        if choice == UserChoice.RETRY:
                            result = self.executor.execute(raw_task, self.user_id)
                            results[-1] = result
                        elif choice == UserChoice.SKIP and task.can_skip:
                            continue
                        else:
                            return {"success": False, "reason": "用户停止"}

            except Exception as e:
                self._notify(f"❌ 异常: {e}")
                if not task.can_skip:
                    return {"success": False, "reason": str(e)}

            # 进度
            self._show_progress(i + 1, len(tasks))

        return {"success": True, "results": results}

    # ====================================================================
    #  交互
    # ====================================================================

    def _notify(self, message: str):
        print(message)

    def _ask_user(self, message: str, options: List[str] = None) -> UserChoice:
        if self.user_callback:
            return self.user_callback(message, options)
        # 默认：自动继续
        return UserChoice.CONTINUE

    def _show_progress(self, current: int, total: int):
        percent = int(current / total * 100) if total > 0 else 0
        filled = int(20 * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (20 - filled)
        self._notify(f"\n📊 [{bar}] {percent}% ({current}/{total})\n")

    def _rollback(self, results: List):
        self._notify("🔄 正在回滚...")
        for r in reversed(results):
            self._notify(f"  撤销: {r.get('task', 'unknown')}")

    # ====================================================================
    #  控制
    # ====================================================================

    def pause(self):
        self.paused = True
        self._notify("⏸️ 任务已暂停，输入「继续」恢复")

    def resume(self):
        self.paused = False
        self._notify("▶️ 任务已恢复")

    def stop(self):
        self.interrupted = True
        self._notify("⏹️ 任务已停止")

    def get_status(self) -> Dict:
        if self.current_plan_id:
            return self.task_manager.get_plan_status(self.current_plan_id)
        return {"status": "idle"}

    @staticmethod
    def _default_callback(message: str, options: List[str] = None) -> UserChoice:
        print(f"\n{message}")
        if options:
            print(f"选项: {', '.join(options)}")
        return UserChoice.CONTINUE


# 使用示例
if __name__ == "__main__":
    orch = UserFriendlyOrchestrator(user_id="test")

    print("=" * 60)
    print("UserFriendlyOrchestrator 测试")
    print("=" * 60)

    for t in ["帮我制作一个关于AI的视频", "帮我写一段排序代码", "你好"]:
        print(f"\n{'='*60}")
        print(f"📥 {t}")
        print(f"{'='*60}")
        result = orch.execute(t)
        print(f"成功: {result.get('success')}")
        print(f"意图: {result.get('intent', 'N/A')}")
        print(f"摘要: {result.get('summary', 'N/A')}")
        if result.get("response"):
            print(f"响应: {result['response'][:300]}")
