#!/usr/bin/env python3
"""Agent 学习基类 - 所有 Agent 的学习能力"""

import json
import time
from pathlib import Path
from datetime import datetime

class BaseLearner:
    def __init__(self, agent_name, domain):
        self.agent_name = agent_name
        self.domain = domain
        self.knowledge_dir = Path(f"/mnt/d/clawsjoy/data/knowledge/{domain}")
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.learned_file = self.knowledge_dir / "learned.json"
        self.load_learned()
    
    def load_learned(self):
        if self.learned_file.exists():
            with open(self.learned_file) as f:
                self.learned = json.load(f)
        else:
            self.learned = {"learned_at": None, "knowledge": [], "stats": {}}
    
    def save_learned(self):
        self.learned["learned_at"] = datetime.now().isoformat()
        with open(self.learned_file, 'w') as f:
            json.dump(self.learned, f, indent=2)
    
    def learn(self, new_knowledge):
        raise NotImplementedError
    
    def get_stats(self):
        return {
            "agent": self.agent_name,
            "domain": self.domain,
            "knowledge_count": len(self.learned.get("knowledge", [])),
            "last_learned": self.learned.get("learned_at")
        }
