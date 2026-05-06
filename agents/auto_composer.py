#!/usr/bin/env python3
"""自动组合 Skills - 根据用户输入动态编排"""

import json
import subprocess
import requests
import re
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"

def analyze_request(user_input):
    """分析用户请求，输出需要的 skills 顺序"""
    
    prompt = f"""分析用户的视频制作需求，输出需要调用的 skills 顺序。

用户需求：{user_input}

可用 skills：
- spider: 采集资料（参数：keyword, city）
- content_writer: 生成脚本（参数：topic, style）
- promo: 制作视频（参数：city, topic, script）

输出格式（JSON）：
{{
    "topic": "提取的话题",
    "city": "城市",
    "workflow": [
        {{"skill": "spider", "params": {{"city": "城市", "keyword": "话题"}}}},
        {{"skill": "content_writer", "params": {{"topic": "话题", "style": "专业"}}}},
        {{"skill": "promo", "params": {{"city": "城市", "topic": "话题"}}}}
    ]
}}

只输出 JSON："""

    resp = requests.post(OLLAMA_URL, json={
        "model": "llama3.2:3b",
        "prompt": prompt,
        "options": {"num_predict": 500}
    })
    
    if resp.status_code == 200:
        text = resp.json().get("response", "")
        # 提取 JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    return {"topic": "香港", "city": "香港", "workflow": []}

def execute_skill(skill_name, params):
    """执行单个 skill"""
    if skill_name == "spider":
        cmd = ['python3', 'skills/spider/execute.py', json.dumps(params)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    
    elif skill_name == "content_writer":
        # 调用 AI 生成脚本
        topic = params.get("topic", "")
        resp = requests.post("http://localhost:8101/api/agent",
            json={"text": f"写一篇300字的文章介绍{topic}，纯文本"})
        return {"script": resp.json().get("message", "")}
    
    elif skill_name == "promo":
        resp = requests.post("http://localhost:8105/api/promo/make",
            json=params, timeout=120)
        return resp.json()
    
    return {"error": "未知 skill"}

def auto_compose(user_input):
    """自动组合执行"""
    print(f"📝 用户需求: {user_input}")
    print("-" * 50)
    
    plan = analyze_request(user_input)
    print(f"🎯 分析结果: {plan.get('topic')} (城市: {plan.get('city')})")
    print(f"📋 工作流: {[s['skill'] for s in plan.get('workflow', [])]}")
    print("-" * 50)
    
    result = None
    for step in plan.get("workflow", []):
        skill = step["skill"]
        params = step.get("params", {})
        print(f"▶️ 执行: {skill}")
        result = execute_skill(skill, params)
        if result.get("video_url"):
            print(f"✅ 视频已生成: {result['video_url']}")
    
    return result

if __name__ == "__main__":
    import sys
    user_input = sys.argv[1] if len(sys.argv) > 1 else "做一个上海人才引进政策的视频"
    result = auto_compose(user_input)
    print(f"\n最终结果: {result}")
