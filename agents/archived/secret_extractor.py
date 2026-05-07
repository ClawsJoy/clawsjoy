#!/usr/bin/env python3
"""智能密钥识别提取器"""

import re
import json
from pathlib import Path

class SecretExtractor:
    """从用户输入中识别密钥"""
    
    PATTERNS = {
        'client_secret': [
            r'"client_secret"\s*:\s*"([^"]+)"',
            r'client_secret\s*=\s*["\']([^"\']+)["\']',
        ],
        'api_key': [
            r'"api_key"\s*:\s*"([^"]+)"',
            r'api_key\s*=\s*["\']([^"\']+)["\']',
        ],
    }
    
    def extract_from_text(self, text):
        results = {}
        for key, patterns in self.PATTERNS.items():
            for p in patterns:
                matches = re.findall(p, text, re.IGNORECASE)
                if matches:
                    results[key] = matches
        return results
    
    def extract_from_json(self, text):
        try:
            data = json.loads(text)
            secrets = {}
            for field in ['client_secret', 'api_key', 'client_id']:
                if field in data:
                    secrets[field] = data[field]
            return secrets
        except:
            return {}
    
    def extract_from_user_input(self, user_input):
        # 尝试 JSON
        if user_input.strip().startswith('{'):
            result = self.extract_from_json(user_input)
            if result:
                return result
        
        # 尝试文本匹配
        return self.extract_from_text(user_input)

if __name__ == "__main__":
    extractor = SecretExtractor()
    
    tests = [
        '{"client_secret":"abc123"}',
        'client_secret = "my_secret"',
    ]
    for t in tests:
        print(f"{t} -> {extractor.extract_from_user_input(t)}")
