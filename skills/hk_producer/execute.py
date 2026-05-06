#!/usr/bin/env python3
"""香港内容生产技能 - 整合采集、脚本、视频"""

import json
import subprocess
import requests
import sys

def execute(params):
    topic = params.get('topic', '香港优才计划')
    
    # 1. 采集资料（调用 spider skill）
    print(f"📡 采集资料: {topic}")
    
    # 2. 生成脚本（调用 AI）
    result = subprocess.run(
        ['ollama', 'run', 'llama3.2:3b', f'写一篇300字的文章介绍{topic}，纯文本'],
        capture_output=True, text=True
    )
    script = result.stdout.strip()
    
    # 3. 清理格式
    import re
    script = re.sub(r'\*\*+', '', script)
    script = re.sub(r'#{3,}', '', script)
    
    print(f"📝 脚本长度: {len(script)}")
    
    # 4. 制作视频（调用 promo API）
    resp = requests.post('http://localhost:8105/api/promo/make',
        json={'topic': topic, 'script': script},
        timeout=120)
    
    return resp.json()

if __name__ == '__main__':
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = execute(params)
    print(json.dumps(result, ensure_ascii=False))
