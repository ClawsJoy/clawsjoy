# tools/log_collector.py - 从你的网关收集日志

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class LogCollector:
    """日志收集器 - 从ClawsJoy的各个模块收集日志"""

    def __init__(self):
        self.log_dirs = [
            Path("logs"),
            Path("data/logs"),
            Path("core/logs"),
        ]

    def get_agent_logs(self, agent_name: str, hours: int = 24) -> List[Dict]:
        """
        获取指定Agent最近N小时的日志

        Args:
            agent_name: Agent名称（chat_agent, code_agent等）
            hours: 最近多少小时
        """
        logs = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # 方法1：从JSONL文件读取
        for log_dir in self.log_dirs:
            log_file = log_dir / f"{agent_name}.jsonl"
            if log_file.exists():
                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            log = json.loads(line)
                            log_time = datetime.fromisoformat(
                                log.get("timestamp", "2000-01-01")
                            )
                            if log_time >= cutoff_time:
                                logs.append(log)
                        except:
                            pass

        # 方法2：从你的reflections.json读取
        reflections_file = Path("data/metacognition/reflections.json")
        if reflections_file.exists():
            with open(reflections_file, "r") as f:
                reflections = json.load(f)
                for ref in reflections:
                    # 根据内容判断是哪个Agent
                    if agent_name in ref.get("user_input", "").lower():
                        logs.append(
                            {
                                "timestamp": ref.get("timestamp"),
                                "success": ref.get("self_assessment") == "good",
                                "input": ref.get("user_input"),
                                "output": ref.get("response"),
                                "feedback": ref.get("feedback"),
                            }
                        )

        return logs

    def get_all_agents_performance(self) -> Dict:
        """获取所有Agent的性能统计"""
        agents = ["chat_agent", "code_agent", "vision_agent", "video_agent"]
        performance = {}

        for agent in agents:
            logs = self.get_agent_logs(agent, hours=168)  # 最近7天
            if logs:
                successes = sum(1 for log in logs if log.get("success", False))
                performance[agent] = {
                    "total": len(logs),
                    "success_rate": successes / len(logs),
                    "sample": logs[-3:] if logs else [],
                }

        return performance
