#!/usr/bin/env python3
"""Metacognition - Metacognition 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from core.lib.config_helper import (
    get_data_root,
    get_embedding_model,
    get_gateway_port,
    get_llm_endpoint,
    get_llm_model,
    get_timeout,
)
from core.lib.unified_config import unified_config

#!/usr/bin/env python3
"""元认知模块 - Agent 自我反思与进化"""

import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class Metacognition:
    """元认知 - Agent 的自我意识"""

    VERSION = "1.0.0"

    def __init__(self, agent_id: str = "default"):
        self.agent_id = agent_id
        self.meta_dir = Path(f"{get_data_root()}/agents/{agent_id}/metacognition")
        self.meta_dir.mkdir(parents=True, exist_ok=True)

        self.reflections_file = self.meta_dir / "reflections.json"
        self.evolutions_file = self.meta_dir / "evolutions.json"
        self._load()

    def _load(self):
        # 加载反思记录
        if self.reflections_file.exists():
            with open(self.reflections_file, "r") as f:
                self.reflections = json.load(f)
        else:
            self.reflections = []

        # 加载进化记录
        if self.evolutions_file.exists():
            with open(self.evolutions_file, "r") as f:
                self.evolutions = json.load(f)
        else:
            self.evolutions = []

    def _save(self):
        with open(self.reflections_file, "w") as f:
            json.dump(self.reflections[-500:], f, indent=2, ensure_ascii=False)
        with open(self.evolutions_file, "w") as f:
            json.dump(self.evolutions, f, indent=2, ensure_ascii=False)

    def reflect(
        self, user_input: str, response: str, user_feedback: Optional[str] = None
    ) -> Dict:
        """反思一次交互"""
        # 自评回答质量
        quality_score = self._assess_quality(response)
        was_helpful = self._was_helpful(response, user_feedback)

        reflection = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input[:200],
            "response": response[:200],
            "quality_score": quality_score,
            "was_helpful": was_helpful,
            "feedback": user_feedback,
            "insight": self._generate_insight(response, quality_score, was_helpful),
        }

        self.reflections.append(reflection)
        self._save()

        return reflection

    def _assess_quality(self, response: str) -> float:
        """评估回答质量 (0-1)"""
        score = 0.5

        # 长度适中
        if 20 < len(response) < 500:
            score += 0.2

        # 有具体内容
        if any(k in response for k in ["Agent", "技能", "系统", "功能"]):
            score += 0.2

        # 不是模板回复
        if "我不知道" not in response and "无法回答" not in response:
            score += 0.1

        return min(1.0, score)

    def _was_helpful(self, response: str, feedback: Optional[str]) -> bool:
        """判断是否有帮助"""
        if feedback:
            return "好" in feedback or "谢谢" in feedback or "正确" in feedback
        return len(response) > 30 and "?" not in response

    def _generate_insight(self, response: str, score: float, helpful: bool) -> str:
        """生成洞察"""
        if score < 0.4:
            return "回答质量偏低，需要更详细的回复"
        elif score < 0.7:
            return "回答基本可用，但可以更精准"
        else:
            return "回答质量良好，继续保持"

    def evolve(self) -> Dict:
        """自我进化 - 从反思中学习"""
        if len(self.reflections) < 10:
            return {"status": "need_more_data", "message": "需要更多交互才能进化"}

        # 计算统计
        recent = self.reflections[-50:]
        avg_score = sum(r["quality_score"] for r in recent) / len(recent)
        helpful_rate = sum(1 for r in recent if r["was_helpful"]) / len(recent)

        # 生成进化建议
        suggestions = []
        if avg_score < 0.5:
            suggestions.append("需要提高回答质量，增加信息量")
        if helpful_rate < 0.6:
            suggestions.append("需要更好地理解用户意图")

        evolution = {
            "timestamp": datetime.now().isoformat(),
            "total_reflections": len(self.reflections),
            "avg_quality_score": round(avg_score, 2),
            "helpful_rate": round(helpful_rate, 2),
            "suggestions": suggestions,
            "version_increment": 0.01 if avg_score > 0.7 else 0,
        }

        self.evolutions.append(evolution)
        self._save()

        return evolution

    def get_stats(self) -> Dict:
        """获取元认知统计"""
        if not self.reflections:
            return {"total": 0}

        recent = self.reflections[-50:]
        return {
            "total_reflections": len(self.reflections),
            "total_evolutions": len(self.evolutions),
            "avg_quality_recent": round(
                sum(r["quality_score"] for r in recent) / len(recent), 2
            ),
            "helpful_rate": round(
                sum(1 for r in recent if r["was_helpful"]) / len(recent), 2
            ),
        }


if __name__ == "__main__":
    meta = Metacognition("test_agent")

    # 模拟反思
    meta.reflect("ClawsJoy 有什么功能？", "ClawsJoy 有10个Agent和20+技能", "很好")
    meta.reflect("你好", "你好", "太简短了")

    print("元认知统计:", meta.get_stats())
    print("进化建议:", meta.evolve())
