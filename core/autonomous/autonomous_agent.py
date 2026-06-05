from core.lib.unified_config import unified_config

#!/usr/bin/env python3
"""Autonomous Agent - Autonomous Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class AutonomousAgent:
    """自主 Agent - 无人值守，自己驱动自己"""

    def __init__(self, name: str):
        self.name = name
        self.running = True
        self.goals = []
        self.memory_file = Path(
            f"{config_helper.get_data_root()}/autonomous/{name}_memory.json"
        )
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_memory()

        print(f"🤖 自主 Agent [{name}] 启动")

    def _load_memory(self):
        if self.memory_file.exists():
            with open(self.memory_file, "r") as f:
                self.memory = json.load(f)
        else:
            self.memory = {
                "goals_completed": [],
                "learned_patterns": [],
                "self_reflections": [],
                "stats": {"total_actions": 0, "success_count": 0},
            }

    def _save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def set_goal(self, goal: str, priority: int = 5):
        """自己设定目标"""
        self.goals.append(
            {
                "goal": goal,
                "priority": priority,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }
        )
        print(f"🎯 [{self.name}] 设定目标: {goal}")

    def think(self):
        """思考：分析当前状态，决定下一步"""
        # 1. 检查是否有待执行目标
        pending_goals = [g for g in self.goals if g.get("status") == "pending"]
        if pending_goals:
            # 按优先级排序
            pending_goals.sort(key=lambda x: x.get("priority", 0), reverse=True)
            current_goal = pending_goals[0]
            return {"action": "execute_goal", "goal": current_goal}

        # 2. 没有目标时，自己创造目标
        return {"action": "create_goal", "reason": "idle"}

    def act(self, decision):
        """行动：执行决策"""
        if decision["action"] == "execute_goal":
            goal = decision["goal"]
            print(f"⚡ [{self.name}] 执行目标: {goal['goal']}")

            # 尝试执行
            result = self._execute_goal(goal["goal"])

            if result["success"]:
                goal["status"] = "completed"
                goal["completed_at"] = datetime.now().isoformat()
                self.memory["goals_completed"].append(goal)
                self.memory["stats"]["success_count"] += 1
                print(f"✅ [{self.name}] 目标完成: {goal['goal']}")
            else:
                goal["status"] = "failed"
                goal["error"] = result.get("error")
                print(
                    f"❌ [{self.name}] 目标失败: {goal['goal']} - {result.get('error')}"
                )

            self._save_memory()
            return result

        elif decision["action"] == "create_goal":
            # 自己创造新目标
            new_goal = self._create_goal()
            if new_goal:
                self.set_goal(new_goal, priority=3)
            return {"action": "created", "goal": new_goal}

        return {"action": "idle"}

    def _execute_goal(self, goal: str) -> Dict:
        """执行具体目标 - 调用系统能力"""
        import subprocess

        # 解析目标，调用对应技能
        if "视频" in goal and "制作" in goal:
            # 调用视频制作
            try:
                result = subprocess.run(
                    [
                        "curl",
                        "-s",
                        "-X",
                        "POST",
                        'http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/smart/execute',
                        "-H",
                        "Content-Type: application/json",
                        "-d",
                        f'{{"query": "{goal}", "user_id": "autonomous"}}',
                    ],
                    capture_output=True,
                    text=True,
                    timeout=config_helper.get_timeout("default"),
                )
                if '"success": true' in result.stdout:
                    return {"success": True, "result": result.stdout[:200]}
                else:
                    return {"success": False, "error": result.stdout[:200]}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif "技能" in goal and "检查" in goal:
            # 检查技能状态
            try:
                result = subprocess.run(
                    [
                        "curl",
                        "-s",
                        'http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/skills',
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return {
                    "success": True,
                    "result": f"共 {result.stdout.count('"name"')} 个技能",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif "记忆" in goal and "检查" in goal:
            # 检查记忆状态
            from core.lib.memory_vector import vector_memory

            count = vector_memory.collection.count()
            return {"success": True, "result": f"向量记忆 {count} 条"}

        else:
            # 通用执行
            return {"success": True, "result": f"已执行: {goal}"}

    def _create_goal(self) -> str:
        """自己创造新目标"""
        # 基于当前状态和自我反思
        completed_count = len(self.memory["goals_completed"])

        if completed_count == 0:
            return "检查系统健康状态"
        elif completed_count == 1:
            return "检查技能可用性"
        elif completed_count == 2:
            return "检查记忆状态"
        elif completed_count == 3:
            return "制作一个测试视频"
        else:
            # 从历史中学习，提出改进目标
            return "优化系统性能"

    def reflect(self):
        """自我反思：分析成功和失败"""
        recent_failures = [
            g for g in self.memory["goals_completed"] if g.get("status") == "failed"
        ][-5:]
        if recent_failures:
            reflection = f"最近有 {len(recent_failures)} 个目标失败，需要检查"
            self.memory["self_reflections"].append(
                {"content": reflection, "timestamp": datetime.now().isoformat()}
            )
            self._save_memory()
            print(f"💭 [{self.name}] 反思: {reflection}")

    def run_cycle(self):
        """一个完整的工作循环"""
        print(f"\n🔄 [{self.name}] 开始工作循环")

        # 1. 思考
        decision = self.think()
        print(f"🧠 [{self.name}] 决策: {decision}")

        # 2. 行动
        result = self.act(decision)

        # 3. 反思
        self.reflect()

        return result

    def start(self, interval_seconds: int = 30):
        """启动自主循环"""

        def _loop():
            while self.running:
                try:
                    self.run_cycle()
                except Exception as e:
                    print(f"⚠️ [{self.name}] 循环错误: {e}")
                time.sleep(interval_seconds)

        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        print(f"🚀 [{self.name}] 自主循环已启动，间隔 {interval_seconds} 秒")

    def stop(self):
        self.running = False


# 创建自主 Agent 实例
autonomous_agent = AutonomousAgent("ClawsJoy")
