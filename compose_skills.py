#!/usr/bin/env python3
"""组合多个 skills"""

import subprocess
import json

def run_skill(skill_name, params):
    """执行单个 skill"""
    cmd = ['python3', f'skills/{skill_name}/execute.py', json.dumps(params)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

# 组合流程
print("1. 采集资料...")
spider_result = run_skill('spider', {'keyword': '香港优才', 'count': 5})

print("2. 生成脚本...")
script_result = run_skill('content_writer', {'topic': '香港优才计划'})

print("3. 制作视频...")
video_result = run_skill('promo', {'city': '香港', 'script': script_result.get('script')})

print(f"✅ 完成: {video_result.get('video_url')}")
