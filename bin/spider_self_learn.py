#!/usr/bin/env python3
"""独立爬虫学习进程"""

import time
import re
from pathlib import Path
import sys
sys.path.insert(0, '/mnt/d/clawsjoy/agents')
from url_scout import URLScout

def learn_from_content():
    scout = URLScout()
    scout.load()
    content_dir = Path("/mnt/d/clawsjoy/data/content")
    new_urls = []
    
    for file in content_dir.glob("*.txt"):
        try:
            with open(file) as f:
                content = f.read()
            urls = re.findall(r'https?://[^\s<>"\']+', content)
            for url in urls[:10]:
                if url not in scout.urls:
                    new_urls.append(url)
        except:
            pass
    
    if new_urls:
        for url in new_urls[:20]:
            scout.urls[url] = {"source": "self_learn", "status": "pending", "discovered_at": time.time()}
        scout.save()
        print(f"🕷️ 发现 {len(new_urls)} 个新 URL")

if __name__ == "__main__":
    while True:
        try:
            learn_from_content()
        except Exception as e:
            print(f"错误: {e}")
        time.sleep(3600)  # 60分钟
