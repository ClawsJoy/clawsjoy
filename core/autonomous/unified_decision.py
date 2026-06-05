from core.lib.unified_config import unified_config

#!/usr/bin/env python3
"""Unified Decision - Unified Decision 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import json
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict

import requests


class DecisionLevel(Enum):
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"


class UnifiedDecisionAgent:
    def __init__(self, name: str = "UnifiedDecision"):
        self.name = name
        self.decision_history = []
        self.data_dir = Path(f"{config_helper.get_data_root()}/autonomous/{name}")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_state()
        print(f"🤖 [{name}] 统一决策 Agent 已启动")

    def _load_state(self):
        state_file = self.data_dir / "state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                data = json.load(f)
                self.decision_history = data.get("history", [])

    def _save_state(self):
        state_file = self.data_dir / "state.json"
        with open(state_file, "w") as f:
            json.dump(
                {"history": self.decision_history[-200:]}, f, indent=2, default=str
            )

    def sense(self) -> Dict:
        status = {"skills": 0, "health": "unknown", "memory": 0, "backend": False}
        try:
            resp = requests.get(
                'http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/health',
                timeout=3,
            )
            if resp.status_code == 200:
                status["backend"] = True
                status["health"] = resp.json().get("status", "unknown")
        except Exception as e:
            status["backend"] = False
        if status["backend"]:
            try:
                resp = requests.get(
                    'http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/skills',
                    timeout=5,
                )
                status["skills"] = resp.json().get("total", 0)
            except Exception as e:
                pass
        try:
            from core.lib.memory_vector import vector_memory

            status["memory"] = vector_memory.collection.count()
        except Exception as e:
            pass
        return status

    def analyze(self, status: Dict) -> Dict:
        issues = []
        if not status["backend"]:
            issues.append("后端服务未运行")
        if status["skills"] < 100:
            issues.append(f"技能数量偏低: {status['skills']}")
        if status["health"] != "ok" and status["backend"]:
            issues.append(f"健康检查异常: {status['health']}")
        level = DecisionLevel.SAFE if not issues else DecisionLevel.WARNING
        return {"issues": issues, "level": level.value, "has_issues": len(issues) > 0}

    def decide(self, analysis: Dict, status: Dict) -> Dict:
        if not analysis["has_issues"]:
            return {
                "action": "idle",
                "target": "none",
                "level": "safe",
                "reason": "系统正常",
            }
        if not status["backend"]:
            return {
                "action": "alert",
                "target": "start_backend",
                "level": "warning",
                "reason": "后端服务未运行，请启动 agent_gateway_web.py",
            }
        for issue in analysis["issues"]:
            if "技能" in issue:
                return {
                    "action": "fix",
                    "target": "sync_skills",
                    "level": "warning",
                    "reason": issue,
                }
            if "健康" in issue:
                return {
                    "action": "check",
                    "target": "health",
                    "level": "safe",
                    "reason": issue,
                }
        return {
            "action": "idle",
            "target": "none",
            "level": "safe",
            "reason": "无需处理",
        }

    def act(self, decision: Dict) -> Dict:
        if decision["action"] == "fix" and "sync" in decision["target"]:
            try:
                resp = requests.post(
                    'http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/knowledge/sync',
                    timeout=10,
                )
                return {
                    "success": True,
                    "result": f"技能同步完成",
                    "code": resp.status_code,
                }
            except Exception as e:
                return {"success": False, "result": str(e)}
        elif decision["action"] == "alert":
            print(f"  ⚠️ 警告: {decision['reason']}")
            return {"success": False, "result": decision["reason"], "need_manual": True}
        return {"success": True, "result": "空闲"}

    def learn(self, decision: Dict, result: Dict, status: Dict):
        self.decision_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "decision": decision,
                "result": result,
            }
        )
        self._save_state()

    def run_cycle(self) -> Dict:
        print(f"\n🔄 [{self.name}] 工作周期")
        status = self.sense()
        print(
            f"  📡 后端:{status['backend']}, 技能:{status['skills']}, 健康:{status['health']}"
        )
        analysis = self.analyze(status)
        print(f"  🔍 问题: {len(analysis['issues'])}")
        decision = self.decide(analysis, status)
        print(f"  🎯 决策: {decision['action']} -> {decision['target']}")
        result = self.act(decision)
        print(
            f"  ⚡ 结果: {'✅' if result['success'] else '⚠️'} {result.get('result', '')[:50]}"
        )
        self.learn(decision, result, status)
        return result


unified_agent = UnifiedDecisionAgent()
