#!/usr/bin/env python3
"""URL 采集 Agent - 自然语言调用"""

import json
import subprocess
import sys

def execute_natural(text):
    """自然语言执行"""
    
    if "采集" in text and ("网站" in text or "URL" in text):
        # 提取 URL
        import re
        url_match = re.search(r'https?://[^\s]+', text)
        if url_match:
            result = subprocess.run(
                ['python3', 'skills/url_collector/execute.py', 
                 json.dumps({"action": "crawl", "url": url_match.group()})],
                capture_output=True, text=True
            )
            return result.stdout
    
    elif "搜索" in text and ("采集源" in text or "分类" in text):
        # 提取分类
        if "移民" in text:
            category = "移民"
        elif "教育" in text:
            category = "教育"
        else:
            category = "通用"
        
        result = subprocess.run(
            ['python3', 'skills/url_collector/execute.py',
             json.dumps({"action": "search", "category": category})],
            capture_output=True, text=True
        )
        return result.stdout
    
    return "未识别指令"

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "采集 https://www.immd.gov.hk/hks/services/index.html"
    print(execute_natural(text))
