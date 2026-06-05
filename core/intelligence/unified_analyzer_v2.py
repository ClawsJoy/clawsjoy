#!/usr/bin/env python3
"""Unified Analyzer V2 - Unified Analyzer V2 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import sys

from core.lib.unified_config import unified_config

sys.path.insert(0, "str(unified_config.ROOT)")
import json

import requests

from core.lib.data_contract import DataContract
from core.lib.memory_simple import memory


class UnifiedAnalyzerV2:
    def __init__(self):
        self.ollama_url = f"http://{unified_config.HOST}:{unified_config.get_port("ollama")}/api/generate"

    def collect_data(self):
        """收集所有数据源"""
        sources = {}
        for cat in memory.memories["categories"].keys():
            items = memory.recall_all(category=cat)
            sources[cat] = {"count": len(items), "samples": items[-2:] if items else []}
        return sources

    def analyze(self):
        sources = self.collect_data()

        prompt = f"""基于以下数据源统计，分析系统问题：
{json.dumps(sources, ensure_ascii=False, indent=2)[:2000]}

输出JSON格式：
{{"summary": "整体评估", "critical_issues": ["问题1", "问题2"], "suggestions": {{}}}}
"""
        resp = requests.post(
            self.ollama_url,
            json={
                "model": unified_config.get_llm_config().get(
                    "default_model",
                    unified_config.get_llm_config().get(
                        "default_model", config_helper.get_llm_model()
                    ),
                ),
                "prompt": prompt,
                "stream": False,
            },
            timeout=config_helper.get_timeout("llm"),
        )
        result = resp.json()["response"]

        import re

        match = re.search(r"\{.*\}", result, re.DOTALL)
        if match:
            analysis = json.loads(match.group())
        else:
            analysis = {"summary": "分析失败", "critical_issues": []}

        # 使用数据契约存储
        DataContract.store_analysis(analysis)
        return analysis


if __name__ == "__main__":
    analyzer = UnifiedAnalyzerV2()
    result = analyzer.analyze()
    print(json.dumps(result, indent=2, ensure_ascii=False))
