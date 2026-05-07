#!/usr/bin/env python3
"""安全 Agent 专属学习 - 敏感模式"""

import re
from pathlib import Path
from base_learner import BaseLearner

class SecurityLearner(BaseLearner):
    def __init__(self):
        super().__init__("security_agent", "security")
        self.sensitive_patterns_file = Path("/mnt/d/clawsjoy/data/sensitive_patterns.json")
    
    def learn(self, new_knowledge=None):
        """学习新的敏感模式"""
        patterns = {
            "api_key": r'api[_-]?key["\s:=]+["\']?([a-zA-Z0-9]{20,})',
            "token": r'token["\s:=]+["\']?([a-zA-Z0-9]{20,})',
            "secret": r'secret["\s:=]+["\']?([a-zA-Z0-9]{20,})',
            "password": r'password["\s:=]+["\']?([^\s"\']{4,})'
        }
        
        knowledge = []
        for name, pattern in patterns.items():
            knowledge.append({
                "type": "sensitive_pattern",
                "name": name,
                "pattern": pattern,
                "learned_at": __import__('time').time()
            })
        
        self.learned["knowledge"] = knowledge
        self.save_learned()
        
        # 保存到独立文件
        with open(self.sensitive_patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2)
        
        return knowledge
    
    def detect_sensitive(self, text):
        """检测敏感信息"""
        found = []
        for item in self.learned.get("knowledge", []):
            matches = re.findall(item["pattern"], text, re.IGNORECASE)
            if matches:
                found.append({
                    "type": item["name"],
                    "matches": matches[:3]
                })
        return found

if __name__ == "__main__":
    learner = SecurityLearner()
    learned = learner.learn()
    print(f"学习了 {len(learned)} 个敏感模式")
    
    test = "api_key=abc123xyz456, token=ya29.abc.xyz"
    detected = learner.detect_sensitive(test)
    print(f"检测到: {detected}")
