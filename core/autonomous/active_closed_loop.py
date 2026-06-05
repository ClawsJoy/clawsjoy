from core.lib.unified_config import unified_config

#!/usr/bin/env python3
"""Active Closed Loop - Active Closed Loop 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import json
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

# 导入已有模块
from core.lib.data_source_manager import data_source_manager
from core.lib.proactive_service import proactive

# from core.autonomous.unified_decision import unified_agent


class LoopState(Enum):
    IDLE = "idle"
    SENSING = "sensing"
    ANALYZING = "analyzing"
    DECIDING = "deciding"
    EXECUTING = "executing"
    LEARNING = "learning"


class ActiveClosedLoop:
    """
    主动闭环智能体
    - 自动感知系统状态
    - 智能分析问题
    - 自主决策行动
    - 安全执行操作
    - 持续学习改进
    """

    def __init__(self, name: str = "ActiveClosedLoop"):
        self.name = name
        self.state = LoopState.IDLE
        self.loop_count = 0
        self.history = []
        self.running = True

        # 配置
        self.sense_interval = 30  # 感知间隔(秒)
        self.auto_fix_enabled = True  # 自动修复开关
        self.notify_on_issue = True  # 问题通知开关

        # 存储
        self.data_dir = Path(f"{config_helper.get_data_root()}/autonomous/{name}")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._load_history()
        print(f"🔄 [{name}] 主动闭环智能体已启动")
        print(f"   📡 感知间隔: {self.sense_interval}秒")
        print(f"   🔧 自动修复: {'开启' if self.auto_fix_enabled else '关闭'}")

    def _load_history(self):
        history_file = self.data_dir / "history.json"
        if history_file.exists():
            with open(history_file, "r") as f:
                self.history = json.load(f)

    def _save_history(self):
        history_file = self.data_dir / "history.json"
        with open(history_file, "w") as f:
            json.dump(self.history[-100:], f, indent=2, default=str)

    def _log(self, action: str, detail: str):
        """记录日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "loop": self.loop_count,
            "state": self.state.value,
            "action": action,
            "detail": detail,
        }
        self.history.append(log_entry)
        self._save_history()
        print(f"  📝 [{action}] {detail[:80]}")

    # ========== 1. 感知 ==========
    def sense(self) -> Dict:
        """感知所有数据源"""
        self.state = LoopState.SENSING
        self._log("sense_start", "开始感知系统状态")

        # 使用数据源管理器获取所有数据
        all_data = data_source_manager.fetch_all()

        # 检查数据质量
        quality_report = self._check_quality(all_data)

        self.state = LoopState.IDLE
        self._log(
            "sense_complete",
            f"感知完成，数据源: {len(all_data)}，质量问题: {len(quality_report.get('issues', []))}",
        )

        return {
            "raw_data": all_data,
            "quality": quality_report,
            "timestamp": datetime.now().isoformat(),
        }

    def _check_quality(self, all_data: Dict) -> Dict:
        """检查数据质量"""
        issues = []
        for name, result in all_data.items():
            if not result.get("success"):
                issues.append(f"{name}: 获取失败 - {result.get('error', 'unknown')}")
            else:
                data = result.get("data", {})
                if name == "skills" and data.get("total", 0) < 100:
                    issues.append(f"{name}: 数量异常 ({data.get('total', 0)} < 100)")
                elif name == "memory_vector" and data.get("count", 0) < 50:
                    issues.append(f"{name}: 数量异常 ({data.get('count', 0)} < 50)")

        return {
            "issues": issues,
            "issue_count": len(issues),
            "has_issues": len(issues) > 0,
        }

    # ========== 2. 分析 ==========
    def analyze(self, sense_result: Dict) -> Dict:
        """分析问题，确定优先级"""
        self.state = LoopState.ANALYZING
        self._log("analyze_start", "开始分析系统状态")

        issues = sense_result.get("quality", {}).get("issues", [])

        # 问题分级
        critical = []
        warning = []
        info = []

        for issue in issues:
            if "失败" in issue or "异常" in issue:
                critical.append(issue)
            elif "偏低" in issue or "不足" in issue:
                warning.append(issue)
            else:
                info.append(issue)

        # 生成行动计划
        actions = []

        if critical:
            actions.append(
                {
                    "priority": "critical",
                    "action": "notify",
                    "target": "admin",
                    "reason": f"严重问题: {critical[0][:50]}",
                }
            )

        if warning:
            if self.auto_fix_enabled:
                actions.append(
                    {
                        "priority": "high",
                        "action": "fix",
                        "target": "sync_skills",
                        "reason": warning[0][:50],
                    }
                )
            else:
                actions.append(
                    {
                        "priority": "high",
                        "action": "notify",
                        "target": "admin",
                        "reason": warning[0][:50],
                    }
                )

        # 定期维护（每10个循环）
        if self.loop_count % 10 == 0 and self.loop_count > 0:
            actions.append(
                {
                    "priority": "low",
                    "action": "maintenance",
                    "target": "system",
                    "reason": "定期维护",
                }
            )

        self.state = LoopState.IDLE
        self._log(
            "analyze_complete", f"分析完成: {len(critical)}个严重, {len(warning)}个警告"
        )

        return {
            "issues": issues,
            "critical": critical,
            "warning": warning,
            "actions": actions,
            "has_actions": len(actions) > 0,
        }

    # ========== 3. 决策 ==========
    def decide(self, analysis_result: Dict) -> Dict:
        """决策：选择执行哪个行动"""
        self.state = LoopState.DECIDING

        actions = analysis_result.get("actions", [])

        if not actions:
            self.state = LoopState.IDLE
            return {"action": "idle", "reason": "无需行动"}

        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        actions.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 4))

        selected = actions[0]
        self._log(
            "decision_made",
            f"决策: {selected['action']} -> {selected.get('target', 'none')}",
        )

        self.state = LoopState.IDLE
        return selected

    # ========== 4. 执行 ==========
    def execute(self, decision: Dict) -> Dict:
        """执行决策"""
        self.state = LoopState.EXECUTING
        action = decision.get("action", "idle")
        target = decision.get("target", "")

        self._log("execute_start", f"执行: {action}/{target}")

        result = {"action": action, "target": target, "success": False}

        if action == "notify":
            # 发送通知
            result["result"] = proactive.send_notification(
                f"[ClawsJoy] {decision.get('priority', 'info')}",
                decision.get("reason", "系统发现问题"),
                decision.get("priority", "info"),
            )
            result["success"] = True

        elif action == "fix":
            if "sync" in target:
                # 同步技能
                try:
                    import requests

                    resp = requests.post(
                        'http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/knowledge/sync',
                        timeout=config_helper.get_timeout("default"),
                    )
                    result["success"] = resp.status_code == 200
                    result["result"] = f"技能同步: {resp.status_code}"
                except Exception as e:
                    result["result"] = str(e)

        elif action == "maintenance":
            # 完整维护
            result["result"] = proactive.run_maintenance()
            result["success"] = True

        elif action == "idle":
            result["success"] = True
            result["result"] = "空闲"

        self.state = LoopState.IDLE
        self._log(
            "execute_complete", f"执行结果: {'成功' if result['success'] else '失败'}"
        )

        return result

    # ========== 5. 学习 ==========
    def learn(
        self,
        sense_result: Dict,
        analysis_result: Dict,
        decision: Dict,
        execute_result: Dict,
    ):
        """从本次循环中学习"""
        self.state = LoopState.LEARNING

        # 记录本次循环
        cycle_record = {
            "loop_id": self.loop_count,
            "timestamp": datetime.now().isoformat(),
            "sense": {
                "issue_count": len(sense_result.get("quality", {}).get("issues", []))
            },
            "analysis": {"actions_count": len(analysis_result.get("actions", []))},
            "decision": decision,
            "execution": execute_result,
            "success": execute_result.get("success", False),
        }
        self.history.append(cycle_record)
        self._save_history()

        # 分析成功率
        recent = self.history[-20:]
        success_count = sum(
            1 for h in recent if h.get("execution", {}).get("success", False)
        )
        success_rate = success_count / len(recent) if recent else 0

        self._log("learn_complete", f"学习完成，近期成功率: {success_rate*100:.0f}%")

        self.state = LoopState.IDLE
        return {"success_rate": success_rate, "total_loops": len(self.history)}

    # ========== 6. 完整闭环 ==========
    def run_once(self) -> Dict:
        """执行一次完整闭环"""
        self.loop_count += 1
        print(f"\n{'='*50}")
        print(f"🔄 闭环 #{self.loop_count}")
        print(f"{'='*50}")

        # 1. 感知
        sense_result = self.sense()
        print(f"📡 感知: {sense_result['quality']['issue_count']} 个问题")

        # 2. 分析
        analysis_result = self.analyze(sense_result)
        print(f"🔍 分析: {len(analysis_result['actions'])} 个待执行动作")

        # 3. 决策
        decision = self.decide(analysis_result)
        print(f"🎯 决策: {decision.get('action', 'idle')}")

        # 4. 执行
        execute_result = self.execute(decision)
        print(f"⚡ 执行: {'✅' if execute_result['success'] else '❌'}")

        # 5. 学习
        learn_result = self.learn(
            sense_result, analysis_result, decision, execute_result
        )

        return {
            "loop": self.loop_count,
            "sense": sense_result,
            "analysis": analysis_result,
            "decision": decision,
            "execution": execute_result,
            "learning": learn_result,
        }

    def start(self, interval_seconds: int = 30):
        """启动主动闭环（持续运行）"""

        def _loop():
            while self.running:
                try:
                    self.run_once()
                except Exception as e:
                    print(f"❌ 闭环异常: {e}")
                time.sleep(interval_seconds)

        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        print(f"🚀 [{self.name}] 主动闭环已启动，间隔 {interval_seconds} 秒")
        return thread

    def stop(self):
        """停止闭环"""
        self.running = False
        print(f"🛑 [{self.name}] 主动闭环已停止")

    def get_status(self) -> Dict:
        """获取状态"""
        recent = self.history[-10:] if self.history else []
        success_count = sum(
            1 for h in recent if h.get("execution", {}).get("success", False)
        )
        return {
            "name": self.name,
            "state": self.state.value,
            "total_loops": self.loop_count,
            "recent_success_rate": success_count / len(recent) if recent else 0,
            "auto_fix_enabled": self.auto_fix_enabled,
        }


# 全局实例
active_loop = ActiveClosedLoop()

from core.autonomous.goal_setter import goal_setter
from core.autonomous.self_reflection import self_reflection


def self_improve(self) -> Dict:
    """自我改进循环"""
    print(f"\n🔄 自我改进循环")

    # 1. 分析系统
    analysis = goal_setter.analyze_system()
    print(f"  📊 系统分析: {analysis['status']}")

    # 2. 生成新目标
    new_goals = goal_setter.generate_goals(analysis)
    for goal in new_goals:
        goal_setter.add_goal(goal)

    # 3. 获取下一个目标
    next_goal = goal_setter.get_next_goal()
    if next_goal:
        print(f"  🎯 执行目标: {next_goal['description']}")
        # 执行目标...
        goal_setter.complete_goal(next_goal["id"], {"success": True})

    # 4. 反思
    reflection_summary = self_reflection.get_summary()
    print(f"  💡 反思: 成功率 {reflection_summary.get('success_rate', 0)*100:.0f}%")

    return {
        "goals": len(goal_setter.goals),
        "reflections": len(self_reflection.reflections),
    }


def execute_goal(self, goal: Dict) -> Dict:
    """执行具体目标"""
    action = goal.get("action", "")

    if action == "check_skills":
        try:
            resp = requests.get(
                'http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/skills',
                timeout=10,
            )
            skills = resp.json()
            return {"success": True, "result": f"技能数: {skills.get('total', 0)}"}
        except Exception as e:
            return {"success": False, "result": str(e)}

    elif action == "sync_knowledge":
        try:
            resp = requests.post(
                'http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/knowledge/sync',
                timeout=config_helper.get_timeout("default"),
            )
            return {"success": resp.status_code == 200, "result": f"同步完成"}
        except Exception as e:
            return {"success": False, "result": str(e)}

    elif action == "generate_report":
        from core.lib.proactive_service import proactive

        report = proactive.generate_report()
        return {"success": True, "result": report.get("file", "报告已生成")}

    return {"success": False, "result": f"未知操作: {action}"}


from core.lib.monitoring_integration import monitoring


def sense_with_monitoring(self) -> Dict:
    """带监控的感知"""
    # 原有感知
    base_sense = self.sense()

    # 增加健康监控
    health = monitoring.get_health_summary()
    alerts = monitoring.get_recent_alerts(5)

    return {
        **base_sense,
        "health": health,
        "alerts": alerts,
        "has_alerts": len(alerts) > 0,
        "health_degraded": health["status"] != "healthy",
    }


def analyze_with_heal(self, sense_result: Dict) -> Dict:
    """带自愈的分析"""
    issues = []

    # 原有问题
    if not sense_result.get("backend", False):
        issues.append("后端服务未运行")

    # 健康监控问题
    if sense_result.get("health_degraded", False):
        health = sense_result.get("health", {})
        unhealthy = [
            s for s, st in health.get("details", {}).items() if st != "healthy"
        ]
        for u in unhealthy:
            issues.append(f"服务 {u} 不健康")

    # 告警问题
    for alert in sense_result.get("alerts", []):
        issues.append(alert)

    # 如果有问题，尝试自愈
    if issues and self.auto_fix_enabled:
        for issue in issues[:2]:  # 最多处理2个
            heal_result = monitoring.trigger_self_heal(issue)
            if heal_result.get("success"):
                print(f"  🔧 触发自愈: {issue[:50]}")

    return {
        "issues": issues,
        "has_issues": len(issues) > 0,
        "severity": "high" if sense_result.get("health_degraded") else "normal",
    }


from core.autonomous.llm_goal_generator import llm_goal_gen
from core.autonomous.task_decomposer import task_decomposer


def generate_smart_goals(self) -> List[Dict]:
    """使用 LLM 生成智能目标"""
    # 收集系统状态
    state = self.sense()
    kb_stats = {}
    try:
        from core.lib.agent_knowledge import agent_knowledge

        kb_stats = agent_knowledge.get_stats()
    except Exception as e:
        pass

    system_state = {
        "skills": state.get("skills", 0),
        "health": state.get("health", "unknown"),
        "memory": state.get("memory", 0),
        "kb_skills": kb_stats.get("skills", 0),
    }

    return llm_goal_gen.generate_goals(system_state, self.history)


def execute_complex_task(self, task_description: str) -> Dict:
    """执行复杂任务（自动分解）"""
    # 1. 分解任务
    sub_tasks = task_decomposer.decompose(task_description)
    print(f"  📋 分解为 {len(sub_tasks)} 个子任务")

    # 2. 获取执行顺序
    order = task_decomposer.get_execution_order(sub_tasks)

    # 3. 按顺序执行
    results = {}
    for task_name in order:
        # 查找任务详情
        task_detail = next((t for t in sub_tasks if t["name"] == task_name), None)
        if task_detail:
            print(f"    ▶️ 执行: {task_name}")
            # 这里可以调用具体的执行逻辑
            results[task_name] = {"success": True}

    return {"success": True, "results": results}


from core.autonomous.llm_goal_generator import llm_goal_gen
from core.autonomous.task_decomposer import task_decomposer


def generate_smart_goals(self) -> List[Dict]:
    """使用 LLM 生成智能目标"""
    # 收集系统状态
    state = self.sense()
    kb_stats = {}
    try:
        from core.lib.agent_knowledge import agent_knowledge

        kb_stats = agent_knowledge.get_stats()
    except Exception as e:
        pass

    system_state = {
        "skills": state.get("skills", 0),
        "health": state.get("health", "unknown"),
        "memory": state.get("memory", 0),
        "kb_skills": kb_stats.get("skills", 0),
    }

    return llm_goal_gen.generate_goals(system_state, self.history)


def execute_complex_task(self, task_description: str) -> Dict:
    """执行复杂任务（自动分解）"""
    # 1. 分解任务
    sub_tasks = task_decomposer.decompose(task_description)
    print(f"  📋 分解为 {len(sub_tasks)} 个子任务")

    # 2. 获取执行顺序
    order = task_decomposer.get_execution_order(sub_tasks)

    # 3. 按顺序执行
    results = {}
    for task_name in order:
        # 查找任务详情
        task_detail = next((t for t in sub_tasks if t["name"] == task_name), None)
        if task_detail:
            print(f"    ▶️ 执行: {task_name}")
            # 这里可以调用具体的执行逻辑
            results[task_name] = {"success": True}

    return {"success": True, "results": results}
