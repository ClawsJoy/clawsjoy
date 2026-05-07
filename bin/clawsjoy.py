#!/usr/bin/env python3
"""ClawsJoy 主入口 - 关键词驱动"""

import json
import sys
import subprocess
from pathlib import Path

def load_keywords():
    with open('/mnt/d/clawsjoy/data/keywords.json', 'r') as f:
        return json.load(f)

def load_categories():
    with open('/mnt/d/clawsjoy/config/hk_categories.json', 'r') as f:
        return json.load(f)

def match_workflow(user_input, categories):
    user_input_lower = user_input.lower()
    for category, info in categories.items():
        for kw in info.get("keywords", []):
            if kw in user_input_lower:
                return {
                    "workflow": "hk_production",
                    "category": category,
                    "style": info.get("风格", "专业"),
                    "keyword": kw
                }
    return {"workflow": "test_flow", "category": "通用", "style": "科技", "keyword": "香港"}

def run_workflow(workflow_name, params):
    """执行工作流"""
    cmd = [sys.executable, "workflow_executor.py", workflow_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "制作香港宣传片"
    categories = load_categories()
    matched = match_workflow(user_input, categories)
    
    print(f"🎯 用户: {user_input}")
    print(f"📌 匹配: {matched['category']} - {matched['keyword']}")
    print(f"🚀 执行工作流: {matched['workflow']}")
    
    # 执行工作流
    output = run_workflow(matched['workflow'], matched)
    print(output)
