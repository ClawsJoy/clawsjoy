#!/usr/bin/env python3
"""Decision Engine V2 - Decision Engine V2 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from core.lib.unified_config import unified_config

#!/usr/bin/env python3
"""智能决策引擎 V2 - 使用统一配置"""
import sys
from core.lib.unified_config import unified_config
sys.path.insert(0, smart_config.ROOT)

import json
import requests
import time
from core.lib.unified_config import config
from core.lib.memory_simple import memory
from datetime import datetime

class IntelligentDecisionEngine:
    def __init__(self):
        self.ollama_url = config.LLM['ollama_endpoint'] + "/api/generate"
        self.default_model = config.LLM['default_model']
        self.fast_model = config.LLM['fast_model']
    
    def decide(self, situation):
        outcomes = memory.recall_all(category='workflow_outcome')[-20:]
        success = len([o for o in outcomes if '成功' in o])
        rate = success / len(outcomes) * 100 if outcomes else 50

        prompt = f"成功率{rate:.0f}%。输出JSON:{{\"decision\":\"决策\",\"action\":\"行动\"}}"

        try:
            resp = requests.post(self.ollama_url, json={
                "model": self.fast_model,
                "prompt": prompt,
                "stream": False
            }, timeout=config_helper.get_timeout("default"))
            result = resp.json().get("response", "")

            import re
            match = re.search(r'\{.*\}', result, re.DOTALL)
            if match:
                decision = json.loads(match.group())
                memory.remember(
                    f"决策执行|成功率{rate:.0f}%|{decision.get('decision')}|行动:{decision.get('action')}",
                    category='executed_decisions'
                )
                return decision
        except Exception as e:
            print(f"决策错误: {e}")

        default = {"decision": "保持现状", "action": "继续监控"}
        memory.remember(
            f"决策执行|成功率{rate:.0f}%|保持现状|行动:继续监控",
            category='executed_decisions'
        )
        return default
    
    def run(self):
        print(f"🧠 决策引擎启动")
        print(f"   LLM: {self.ollama_url}")
        print(f"   模型: {self.default_model} / {self.fast_model}")

        while True:
            decision = self.decide("系统状态")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {decision}")
            time.sleep(3600)

if __name__ == "__main__":
    engine = IntelligentDecisionEngine()
    engine.run()
