"""安全护栏 - 价值观对齐、内容过滤、合规保障"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict

class SafetyGuard:
    def __init__(self):
        self.rules_file = Path("data/safety_rules.json")
        self.rules = self._load_rules()
        self.violation_log = Path("logs/safety_violations.log")
        self.violation_log.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_rules(self) -> Dict:
        if self.rules_file.exists():
            with open(self.rules_file, 'r') as f:
                return json.load(f)
        return self._default_rules()
    
    def _default_rules(self) -> Dict:
        return {
            "patterns": {
                "violence": [r"杀.*人", r"暴力", r"how to kill", r"violent"],
                "illegal": [r"炸弹", r"入侵", r"盗取", r"hack", r"steal"],
                "personal": [r"\d{17}[\dXx]", r"1[3-9]\d{9}"],
            },
            "safe_responses": {
                "violence": "我无法提供关于暴力的内容。",
                "illegal": "我不能协助任何违法活动。",
                "personal": "为了保护隐私，我不会处理个人敏感信息。"
            },
            "enabled": True
        }
    
    def check_input(self, text: str) -> Tuple[bool, str, str]:
        if not self.rules.get("enabled", True):
            return True, "", ""
        
        for category, patterns in self.rules["patterns"].items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return False, category, self.rules["safe_responses"].get(category, "内容不合规")
        return True, "", ""
    
    def check_output(self, text: str) -> Tuple[bool, str]:
        for category, patterns in self.rules["patterns"].items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return False, self.rules["safe_responses"].get(category, "内容不合规")
        return True, ""
    
    def get_stats(self) -> Dict:
        return {"enabled": self.rules.get("enabled", True)}

safety_guard = SafetyGuard()
