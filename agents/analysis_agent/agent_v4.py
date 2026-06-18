#!/usr/bin/env python3
"""AnalysisAgent v4.2 - 精简稳定版（数据分析）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class AnalysisAgentV4(BusinessAgent):
    """数据分析 Agent - 精简稳定版"""

    name = "analysis_agent_v4"
    description = "智慧数据分析助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._llm_model = "qwen2.5:7b"
        print(f"📊 AnalysisAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        
        if any(kw in t for kw in ["分析", "数据分析", "统计", "趋势"]):
            return self._resp(self._analyze(user_input))
        
        if any(kw in t for kw in ["总结", "摘要", "概括"]):
            return self._resp(self._summarize(user_input))
        
        return self._resp(f"📊 我是数据分析助手。输入「分析 + 数据」或「总结 + 内容」开始。")

    # ================================================================
    #  分析
    # ================================================================

    def _analyze(self, text: str) -> str:
        data = self._extract_data(text)
        analysis_type = self._identify_analysis_type(text)
        
        if data:
            prompt = f"""分析以下数据：

数据：{data}
类型：{analysis_type}

输出：概览、趋势、异常、洞察、建议（Markdown格式）
"""
        else:
            prompt = f"""
用户想分析：{text}

请以提问方式引导用户提供数据，输出：

## 🔍 需要以下信息

### 必需数据
1. xxx - 原因

### 输出
分析完成后将获得：xxx

请提供数据。
"""
        result = self._call_llm(prompt)
        return result or "📊 请提供需要分析的数据。"

    # ================================================================
    #  总结
    # ================================================================

    def _summarize(self, text: str) -> str:
        content = re.sub(r'^(总结|摘要|概括)', '', text).strip()
        if not content:
            return "📝 请提供要总结的内容。"
        
        prompt = f"总结以下内容（3-5个要点）：{content}"
        result = self._call_llm(prompt)
        return f"📝 摘要\n\n{result}" if result else "总结生成失败。"

    # ================================================================
    #  辅助方法
    # ================================================================

    def _extract_data(self, text: str) -> str:
        match = re.search(r'数据[：:]\s*([^\n]+)', text)
        if match:
            return match.group(1).strip()
        match = re.search(r'```(?:json|csv|table)?\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        if len(numbers) >= 3:
            return f"数字: {', '.join(numbers)}"
        return ""

    def _identify_analysis_type(self, text: str) -> str:
        t = text.lower()
        if any(kw in t for kw in ["销售", "销售额", "销量"]):
            return "sales"
        if any(kw in t for kw in ["用户", "客户", "活跃"]):
            return "user"
        if any(kw in t for kw in ["财务", "收入", "成本", "利润"]):
            return "financial"
        return "general"

    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self._llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 500}
                },
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"[Analysis] LLM失败: {e}")
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = AnalysisAgentV4("test")
    print(agent.process("分析销售数据")["response"])
