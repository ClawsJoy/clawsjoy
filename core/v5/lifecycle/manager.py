#!/usr/bin/env python3
"""Manager - Manager 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


from datetime import datetime
from enum import Enum
from typing import Dict, List


class AgentState(Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    DEGRADED = "degraded"
    STOPPED = "stopped"


class LifecycleManager:
    """生命周期管理器 - 6/6 闭环"""

    PHASES = ["perceive", "decide", "act", "monitor", "learn", "evolve"]

    def __init__(self):
        self.agent_states: Dict[str, AgentState] = {}
        self.phase_history: List[Dict] = []
        self._metrics: Dict[str, List[float]] = {}

    def register_agent(self, agent_name: str):
        self.agent_states[agent_name] = AgentState.INITIALIZING
        self._record_phase(agent_name, "registered")

    def transition(self, agent_name: str, new_state: AgentState):
        old_state = self.agent_states.get(agent_name)
        self.agent_states[agent_name] = new_state
        self._record_phase(agent_name, f"transition: {old_state} -> {new_state}")

    def record_metric(self, agent_name: str, metric_name: str, value: float):
        key = f"{agent_name}_{metric_name}"
        if key not in self._metrics:
            self._metrics[key] = []
        self._metrics[key].append(value)
        if len(self._metrics[key]) > 100:
            self._metrics[key] = self._metrics[key][-100:]

    def get_health_score(self, agent_name: str) -> float:
        key = f"{agent_name}_response_time"
        if key in self._metrics and self._metrics[key]:
            avg_time = sum(self._metrics[key][-10:]) / len(self._metrics[key][-10:])
            return max(0, min(100, 100 - avg_time * 10))
        return 85.0

    def _record_phase(self, agent_name: str, event: str):
        self.phase_history.append(
            {
                "agent": agent_name,
                "event": event,
                "timestamp": datetime.now().isoformat(),
            }
        )
        if len(self.phase_history) > 1000:
            self.phase_history = self.phase_history[-1000:]

    def get_agent_state(self, agent_name: str) -> str:
        state = self.agent_states.get(agent_name, AgentState.STOPPED)
        return state.value

    def get_phases(self) -> List[str]:
        return self.PHASES

    def get_history(self, agent_name: str = None, limit: int = 50) -> List[Dict]:
        history = self.phase_history
        if agent_name:
            history = [h for h in history if h["agent"] == agent_name]
        return history[-limit:]


lifecycle = LifecycleManager()
