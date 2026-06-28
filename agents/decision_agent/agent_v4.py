#!/usr/bin/env python3
"""DecisionAgent v4.2 - 精简稳定版（路由决策）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from core.agents.business.business_agent import BusinessAgent


class DecisionAgentV4(BusinessAgent):
    """路由决策 Agent - 精简稳定版"""

    name = "decision_agent_v4"
    description = "智慧决策者"
    version = "5.0.0"

    AGENT_CAPABILITIES = {
        "chat_agent": ["聊天", "对话", "问答"],
        "code_agent": ["代码", "编程", "函数", "debug"],
        "analysis_agent": ["分析", "数据", "统计", "趋势"],
        "butler_agent": ["待办", "提醒", "日程"],
        "translate_agent": ["翻译"],
        "calculator_agent": ["计算", "数学"],
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._data_dir = Path(f"data/decision_learning/{user_id}")
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._calibration_data = self._load_calibration()
        print(f"🎖 DecisionAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心决策逻辑"""
        result = self.decide(user_input)
        return self._resp(f"🎯 推荐 Agent: **{result.get('agent')}**\n\n理由: {result.get('reasoning', '')}")

    # ================================================================
    #  核心决策
    # ================================================================

    def decide(self, task: str, candidates: List[str] = None) -> Dict:
        scores = self._keyword_match(task)
        
        # 如果有候选，筛选
        if candidates:
            scores = [s for s in scores if s["agent"] in candidates]
        
        if not scores:
            return {"agent": "chat_agent", "confidence": 0.5, "reasoning": "默认选择"}
        
        best = scores[0]
        return {
            "agent": best["agent"],
            "confidence": best["confidence"],
            "reasoning": best["reasoning"],
            "alternatives": [s["agent"] for s in scores[1:3]] if len(scores) > 1 else []
        }

    # ================================================================
    #  关键词匹配
    # ================================================================

    def _keyword_match(self, task: str) -> List[Dict]:
        t = task.lower()
        results = []
        
        for agent, keywords in self.AGENT_CAPABILITIES.items():
            matched = [kw for kw in keywords if kw in t]
            score = min(len(matched) / 2, 1.0)
            results.append({
                "agent": agent,
                "confidence": score,
                "reasoning": f"匹配: {', '.join(matched)}" if matched else "无关键词匹配"
            })
        
        # 语义消歧：防止明显的误匹配
        DISAMBIGUATION = {
            "code_agent": {
                "写诗": 0, "写歌": 0, "写小说": 0, "写文章": 0, "写作文": 0,
                "写日记": 0, "写故事": 0, "写剧本": 0, "写信": 0, "写邮件": 0,
            },
            "calculator_agent": {
                "日历": 0, "日期": 0, "星期": 0, "时间": 0,
            },
        }
        
        for r in results:
            agent = r["agent"]
            if agent in DISAMBIGUATION:
                for keyword, penalty in DISAMBIGUATION[agent].items():
                    if keyword in t:
                        r["confidence"] = penalty
                        r["reasoning"] = f"语义消歧: '{keyword}' 不应路由到 {agent}"
        
        return sorted(results, key=lambda x: x["confidence"], reverse=True)

    # ================================================================
    #  加载校准数据
    # ================================================================

    def _load_calibration(self) -> Dict:
        cal_file = self._data_dir / "calibration.json"
        if cal_file.exists():
            try:
                with open(cal_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = DecisionAgentV4("test")
    print(agent.process("帮我写一段代码")["response"])
