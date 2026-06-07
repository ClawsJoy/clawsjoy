#!/usr/bin/env python3
"""智能升级器 V2 - 针对超时问题的专项优化"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

from core.agents.builtin.config_upgrader import ConfigUpgrader


class SmartUpgraderV2(ConfigUpgrader):
    """智能升级器 - 专项优化超时问题"""

    def analyze_timeout_issue(self, logs: List[Dict]) -> Dict:
        """专项分析超时问题"""
        timeouts = [
            log for log in logs if "timeout" in str(log.get("error", "")).lower()
        ]

        if not timeouts:
            return {"has_timeout_issue": False}

        # 分析超时时的平均输入长度
        avg_input_len = sum(len(log.get("input", "")) for log in timeouts) / len(
            timeouts
        )

        return {
            "has_timeout_issue": True,
            "timeout_count": len(timeouts),
            "timeout_rate": len(timeouts) / len(logs),
            "avg_input_length": avg_input_len,
            "suggestion": self._get_timeout_suggestion(avg_input_len),
        }

    def _get_timeout_suggestion(self, avg_input_len: float) -> Dict:
        """根据输入长度给出建议"""
        if avg_input_len < 50:
            return {
                "issue": "短请求超时",
                "suggestion": "检查模型加载时间，考虑使用更小的模型",
                "params": {"max_tokens": 512},
            }
        elif avg_input_len < 200:
            return {
                "issue": "中等请求超时",
                "suggestion": "增加max_tokens，优化提示词",
                "params": {"max_tokens": 2048},
            }
        else:
            return {
                "issue": "长请求超时",
                "suggestion": "需要分段处理或使用更强大的模型",
                "params": {"max_tokens": 4096},
            }

    def upgrade_agent(
        self, agent_name: str, logs: List[Dict], auto_apply: bool = False
    ) -> Dict:
        """智能升级 - 针对超时问题的专项优化"""

        # 首先分析超时问题
        timeout_analysis = self.analyze_timeout_issue(logs)

        if timeout_analysis.get("has_timeout_issue"):
            print(f"   ⏰ 检测到超时问题: {timeout_analysis['timeout_rate']:.1%}")
            print(f"   💡 {timeout_analysis['suggestion']['suggestion']}")

            # 专项优化：调整max_tokens
            suggested_params = timeout_analysis["suggestion"]["params"]

            # 读取当前配置
            config_file = Path(f"agents/{agent_name}/config.yaml")
            if config_file.exists():
                with open(config_file, "r") as f:
                    config = yaml.safe_load(f)

                current_max_tokens = (
                    config.get("agent", {}).get("llm", {}).get("max_tokens", 1024)
                )
                suggested_max_tokens = suggested_params.get(
                    "max_tokens", current_max_tokens
                )

                if suggested_max_tokens != current_max_tokens:
                    print(
                        f"   📝 调整 max_tokens: {current_max_tokens} → {suggested_max_tokens}"
                    )

                    if auto_apply:
                        # 备份并修改配置
                        backup_file = config_file.with_suffix(".yaml.bak")
                        import shutil

                        shutil.copy2(config_file, backup_file)

                        config["agent"]["llm"]["max_tokens"] = suggested_max_tokens
                        with open(config_file, "w") as f:
                            yaml.dump(
                                config, f, allow_unicode=True, default_flow_style=False
                            )

                        return {
                            "upgraded": True,
                            "reason": f"超时优化: max_tokens {current_max_tokens} → {suggested_max_tokens}",
                            "changes": {"max_tokens": suggested_max_tokens},
                        }

        # 如果没有超时问题或无法优化，使用默认升级
        return super().upgrade_agent(agent_name, logs, auto_apply)


if __name__ == "__main__":
    upgrader = SmartUpgraderV2()

    # 测试
    from tools.real_log_collector import RealLogCollector

    collector = RealLogCollector()

    for agent in ["chat_agent", "code_agent", "vision_agent"]:
        logs = collector.collect_agent_logs(agent, hours=24)
        if logs:
            result = upgrader.upgrade_agent(agent, logs, auto_apply=True)
            print(f"\n{agent}: {result}")
