#!/usr/bin/env python3
"""Decision Engine V4 - Decision Engine V4 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from core.lib.config_loader import config
from core.lib.llm_config import llm_config


class DecisionEngineV4:
    VERSION = "4.0.0"
    
    def __init__(self):
        # 使用配置驱动
        self.ollama_url = llm_config.get_ollama_url()
        self.ollama_model = llm_config.get_ollama_model()
        self.decision_file = Path(config.get_path('data')) / "decisions.json"
        self.decision_history = self._load_history()
    
    def _load_history(self) -> list:
        if self.decision_file.exists():
            try:
                with open(self.decision_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self):
        with open(self.decision_file, 'w') as f:
            json.dump(self.decision_history[-1000:], f, indent=2)
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """做出决策"""
        task_name = context.get('task_name', '')

        # 基于规则的快速决策
        if '热度100' in task_name:
            decision = {"action": "execute", "priority": "high", "confidence": 0.9}
        elif '热度' in task_name:
            decision = {"action": "execute", "priority": "normal", "confidence": 0.7}
        else:
            decision = {"action": "defer", "priority": "low", "confidence": 0.5}

        # 记录决策
        decision["task"] = task_name
        decision["timestamp"] = datetime.now().isoformat()
        self.decision_history.append(decision)
        self._save_history()

        return decision
    
    def get_stats(self) -> Dict:
        return {
            "version": self.VERSION,
            "ollama_url": self.ollama_url,
            "ollama_model": self.ollama_model,
            "total_decisions": len(self.decision_history)
        }


decision_engine = DecisionEngineV4()
