#!/usr/bin/env python3
"""大脑连接器"""

import json
from pathlib import Path
from datetime import datetime

class BrainConnector:
    def __init__(self):
        self.brain_file = Path("/mnt/d/clawsjoy/data/agent_brain.json")
        self.brain = self._load()
        self.llm_connected = False
    
    def _load(self):
        if self.brain_file.exists():
            try:
                return json.load(open(self.brain_file))
            except:
                return {"experiences": [], "best_practices": []}
        return {"experiences": [], "best_practices": []}
    
    def record_experience(self, agent: str, action: str, result: dict, context: str = ""):
        self.brain.setdefault("experiences", []).append({
            "agent": agent, "action": action, "result": result,
            "context": context[:200], "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False)
        })
        if len(self.brain["experiences"]) > 200:
            self.brain["experiences"] = self.brain["experiences"][-200:]
        with open(self.brain_file, 'w') as f:
            json.dump(self.brain, f, indent=2)
    
    def add_best_practice(self, practice: str, agent: str, tags: list = None):
        self.brain.setdefault("best_practices", []).append({
            "practice": practice, "agent": agent, "tags": tags or [],
            "created_at": datetime.now().isoformat()
        })
        with open(self.brain_file, 'w') as f:
            json.dump(self.brain, f, indent=2)
    
    def get_stats(self):
        return {
            "brain_experiences": len(self.brain.get("experiences", [])),
            "best_practices": len(self.brain.get("best_practices", []))
        }


    def query_llm(self, prompt: str) -> str:
        """查询本地 LLM"""
        if not self.llm_connected:
            return ""
        try:
            import requests
            resp = requests.post(f"{self.ollama_url}/api/generate", json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except:
            pass
        return ""
