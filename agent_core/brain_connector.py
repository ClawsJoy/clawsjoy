from lib.unified_config import config
#!/usr/bin/env python3
"""大脑连接器 - ClawsJoy Agent 核心"""

import json
import requests
from pathlib import Path
from datetime import datetime

class BrainConnector:
    def __init__(self):
        self.root = Path("/mnt/d/clawsjoy")
        self.brain_file = self.root / "data" / "agent_brain.json"
        self.ollama_url = "http://localhost:11434"
        self.model = config.LLM["default_model"]
        self.brain = self._load()
        self.llm_connected = self._check_llm()
    
    def _load(self):
        if self.brain_file.exists():
            try:
                return json.load(open(self.brain_file))
            except:
                return {"experiences": [], "best_practices": []}
        return {"experiences": [], "best_practices": []}
    
    def _check_llm(self):
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                tags = resp.json().get("models", [])
                for m in tags:
                    if self.model in m.get("name", ""):
                        return True
            return False
        except:
            return False
    
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
    
    def query_llm(self, prompt: str) -> str:
        if not self.llm_connected:
            return ""
        try:
            resp = requests.post(f"{self.ollama_url}/api/generate", json={
                "model": self.model, "prompt": prompt, "stream": False
            }, timeout=60)
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"LLM 错误: {e}")
        return ""
    
    def get_stats(self):
        return {
            "brain_experiences": len(self.brain.get("experiences", [])),
            "best_practices": len(self.brain.get("best_practices", [])),
            "llm_connected": self.llm_connected
        }

brain_connector = BrainConnector()
