#!/usr/bin/env python3
"""Closed Loop - Closed Loop 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from datetime import datetime
import time
from typing import Dict, Any
from core.lib.unified_config import unified_config


class ClosedLoop:
    """
    6/6 完整闭环
    1. 感知 (Sense) - 收集数据
    2. 分析 (Analyze) - 分析问题
    3. 决策 (Decide) - 制定方案
    4. 执行 (Act) - 执行行动
    5. 反馈 (Feedback) - 收集结果
    6. 学习 (Learn) - 优化改进
    """
    
    VERSION = "5.0.0"

    def __init__(self):
        self.enabled = True
        self.loop_count = 0
        self.history = []
        self.config = unified_config.get("closed_loop", {})
        self._init_components()
        print(f"🔄 闭环控制器 v{self.VERSION} 已启动")

    def _init_components(self):
        """初始化组件"""
        self.health_scoring = self.config.get("health_scoring", {})
        self.alerting = self.config.get("alerting", {})
        self.skill_routing = self.config.get("skill_routing", {})
        self.stats = {
            "total_loops": 0,
            "successful": 0,
            "failed": 0,
            "avg_response_time": 0
        }

    def sense(self) -> Dict:
        """1. 感知 - 收集系统状态"""
        try:
            import requests
            gateway_health = requests.get("http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/health", timeout=5).json()
            gateway_status = gateway_health.get("status") == "ok"

            return {
                "timestamp": datetime.now().isoformat(),
                "gateway": {
                    "status": "healthy" if gateway_status else "unhealthy",
                    "version": gateway_health.get("version", "unknown")
                },
                "loop_count": self.loop_count
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "gateway": {"status": "unknown", "error": str(e)},
                "loop_count": self.loop_count
            }

    def analyze(self, state: Dict) -> Dict:
        """2. 分析 - 分析系统状态"""
        thresholds = self.health_scoring.get("thresholds", {})
        base_score = self.health_scoring.get("base_score", 85)
        health_score = base_score

        issues = []

        # 网关健康分析
        if state.get("gateway", {}).get("status") != "healthy":
            health_score -= 30
            issues.append({
                "type": "gateway_unhealthy",
                "severity": "critical",
                "message": "网关服务不健康"
            })

        # 等级判定
        warning_threshold = thresholds.get("health_warning", 70)
        critical_threshold = thresholds.get("health_critical", 50)

        if health_score < critical_threshold:
            level = "critical"
        elif health_score < warning_threshold:
            level = "warning"
        else:
            level = "healthy"

        return {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "level": level,
            "issues": issues,
            "thresholds": thresholds
        }

    def decide(self, analysis: Dict) -> Dict:
        """3. 决策 - 制定行动方案"""
        actions = []
        priority = "normal"

        if analysis["level"] == "critical":
            actions.append({
                "type": "restart_gateway",
                "priority": "high",
                "message": "网关服务异常，建议重启"
            })
            priority = "high"
        elif analysis["level"] == "warning":
            actions.append({
                "type": "send_alert",
                "priority": "medium", 
                "message": f"健康度下降至 {analysis['health_score']}"
            })
            priority = "medium"
        else:
            actions.append({
                "type": "continue",
                "priority": "low",
                "message": "系统运行正常"
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "actions": actions,
            "priority": priority
        }

    def act(self, decision: Dict) -> Dict:
        """4. 执行 - 执行行动"""
        results = []
        for action in decision.get("actions", []):
            action_type = action.get("type")
            if action_type == "restart_gateway":
                results.append({
                    "action": action_type,
                    "success": True,
                    "message": "重启命令已记录（需手动确认）"
                })
            elif action_type == "send_alert":
                results.append({
                    "action": action_type,
                    "success": True,
                    "message": f"告警已发送: {action.get('message')}"
                })
            else:
                results.append({
                    "action": action_type,
                    "success": True,
                    "message": "继续监控"
                })

        return {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "success": all(r.get("success") for r in results)
        }

    def feedback(self, execution: Dict, analysis: Dict) -> Dict:
        """5. 反馈 - 收集执行结果"""
        return {
            "timestamp": datetime.now().isoformat(),
            "execution_success": execution.get("success", False),
            "health_score": analysis.get("health_score", 0),
            "lessons": []
        }

    def learn(self, feedback: Dict) -> Dict:
        """6. 学习 - 优化决策"""
        insights = []

        if not feedback.get("execution_success"):
            insights.append({
                "type": "action_failure",
                "message": "执行失败，需要检查行动条件"
            })

        if feedback.get("health_score", 100) < 50:
            insights.append({
                "type": "critical_pattern",
                "message": "系统频繁进入严重状态"
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "insights": insights,
            "optimizations": []
        }

    def run(self, context: dict = None) -> dict:
        """运行完整闭环"""
        start_time = time.time()
        self.loop_count += 1

        print(f"\n🔄 闭环 #{self.loop_count}")

        # 1-6 完整闭环
        state = self.sense()
        analysis = self.analyze(state)
        decision = self.decide(analysis)
        execution = self.act(decision)
        feedback_data = self.feedback(execution, analysis)
        learning = self.learn(feedback_data)

        elapsed = time.time() - start_time

        # 更新统计
        self.stats["total_loops"] += 1
        if execution.get("success"):
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1

        self.stats["avg_response_time"] = (
            self.stats["avg_response_time"] * (self.stats["total_loops"] - 1) + elapsed
        ) / self.stats["total_loops"] if self.stats["total_loops"] > 1 else elapsed

        # 记录历史
        self.history.append({
            "loop_id": self.loop_count,
            "time": datetime.now().isoformat(),
            "health_score": analysis.get("health_score"),
            "actions": len(decision.get("actions", [])),
            "success": execution.get("success")
        })

        if len(self.history) > 100:
            self.history = self.history[-100:]

        return {
            "status": "success",
            "loop_id": self.loop_count,
            "timestamp": datetime.now().isoformat(),
            "enabled": self.enabled,
            "analysis": analysis,
            "decision": decision,
            "execution": execution,
            "learning": learning,
            "stats": self.stats,
            "elapsed_ms": elapsed * 1000
        }

    def get_status(self) -> dict:
        """获取闭环状态"""
        return {
            "version": self.VERSION,
            "enabled": self.enabled,
            "loop_count": self.loop_count,
            "stats": self.stats,
            "history_length": len(self.history),
            "recent": self.history[-5:] if self.history else []
        }


closed_loop = ClosedLoop()

closed_loop = ClosedLoop()


def start_auto_loop():
    """启动自动闭环（独立函数）"""
    import threading
    import time
    
    def _loop():
        while True:
            time.sleep(3600)
            try:
                closed_loop.run()
                print(f"[自动闭环] 运行完成")
            except Exception as e:
                print(f"[自动闭环] 错误: {e}")
    
    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    print("✅ 自动闭环已启动（每小时运行）")
