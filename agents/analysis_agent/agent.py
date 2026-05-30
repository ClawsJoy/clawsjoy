#!/usr/bin/env python3
"""Agent - Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import logging

"""数据分析师 - 情报官"""

import json
import re
from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter


class AnalysisAgent(SmartAgent):
    """数据分析师 - 情报官"""

    name = "analysis_agent"
    description = "数据分析与建议"
    type = "core"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"📊 分析师 已上岗")

    def process(self, user_input: str, context=None) -> Dict:
        print(f"[分析师] 收到: {user_input}")

        # 1. 分析意图
        analysis = self._analyze_intent(user_input)

        # 2. 如果需要决策，调用决策师
        if analysis.get("need_decision", False):
            result = self._call_decision_maker(analysis)
            return result

        # 3. 记录交互
        self.record_interaction(user_input, analysis.get("report", ""))

        return {
            "success": True,
            "response": analysis.get("report", "分析完成"),
            "analysis": analysis,
            "agent": self.name,
            "user_id": self.user_id
        }

    def _analyze_intent(self, text: str) -> Dict:
        """分析意图"""
        prompt = f"""分析用户输入，返回 JSON 格式。

用户输入: {text}

输出格式:
{{
    "intent": "calculation/dialect/chat/question",
    "need_calculation": true/false,
    "need_dialect": true/false,
    "need_decision": true/false,
    "confidence": 0.0-1.0,
    "report": "分析报告"
}}"""

        try:
            response = smart_adapter.generate(prompt, auto_select=True)
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error: {e}", exc_info=True)
            pass

        return {
            "intent": "chat",
            "need_calculation": False,
            "need_dialect": False,
            "need_decision": False,
            "confidence": 0.5,
            "report": "已收到您的消息"
        }

    def _call_decision_maker(self, analysis: Dict) -> Dict:
        """调用决策师"""
        import requests
        
        print(f"[分析师] 调用决策师: {analysis.get('intent')}")
        
        try:
            resp = requests.post(
                "http://localhost:5002/api/agent/decision_agent/message",
                json={"message": analysis.get("report", ""), "user_id": self.user_id},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"success": False, "error": f"决策师调用失败: HTTP {resp.status_code}"}
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


analysis_agent = AnalysisAgent()
