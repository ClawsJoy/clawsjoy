#!/usr/bin/env python3
"""Analysis Agent - 数据分析师"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter


class AnalysisAgent(SmartAgent):
    name = "analysis_agent"
    description = "数据分析师，负责数据分析和报告"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_agent_config()
        print("📊 分析师 已上岗")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[分析师] 收到: {user_input}")

        # 如果是图片分析请求，转发给 vision_agent
        if any(kw in user_input.lower() for kw in ['.png', '.jpg', '.jpeg', '图片', '识别']):
            try:
                from core.agents.builtin.vision_agent import VisionAgent
                vision = VisionAgent(self.user_id)
                result = vision.process(user_input)
                return {
                    "success": True,
                    "response": result.get('response', ''),
                    "agent": self.name,
                    "tool": "vision_agent",
                    "user_id": self.user_id
                }
            except Exception as e:
                print(f"调用 vision_agent 失败: {e}")

        # 默认使用 LLM 分析
        result = smart_adapter.generate(
            user_input,
            model=self.llm_model,
            temperature=self.llm_temperature
        )

        return {
            "success": True,
            "response": result,
            "agent": self.name,
            "user_id": self.user_id
        }
