#!/usr/bin/env python3
"""自然语言添加 URL 采集源"""

import sys
import re
import json
import subprocess

def parse_and_add(text):
    # 提取 URL
    url_match = re.search(r'https?://[^\s]+', text)
    if not url_match:
        return "未找到 URL"
    
    url = url_match.group()
    
    # 提取名称
    name_match = re.search(r'([^，,]+)(?:网站|官网|的网站)', text)
    name = name_match.group(1) if name_match else url.split('/')[2]
    
    # 提取分类
    category = "通用"
    if "移民" in text or "签证" in text:
        category = "移民"
    elif "教育" in text or "留学" in text:
        category = "教育"
    elif "工作" in text or "招聘" in text:
        category = "工作"
    elif "医疗" in text or "医院" in text:
        category = "医疗"
    elif "住房" in text or "租房" in text:
        category = "住房"
    elif "旅游" in text or "美食" in text:
        category = "旅游"
    
    # 添加
    result = subprocess.run(
        ['python3', 'skills/url_collector/execute.py',
         json.dumps({"action": "add", "name": name, "url": url, "category": category})],
        capture_output=True, text=True
    )
    return f"✅ 已添加: {name} ({category})\n{result.stdout}"

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "添加香港房屋署网站 https://www.housingauthority.gov.hk/"
    print(parse_and_add(text))
