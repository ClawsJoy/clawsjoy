#!/usr/bin/env python3
"""智能采集控制器 - Agent 决定采集什么、从哪里采"""

import json
import requests
import subprocess

# 预设采集源
SOURCES = {
    "香港": {
        "新闻": "https://www.info.gov.hk/gia/general/today.htm",
        "入境处": "https://www.immd.gov.hk/hks/faq/index.html",
        "人才政策": "https://www.hkqf.gov.hk/"
    },
    "上海": {
        "人才政策": "https://www.shanghai.gov.cn/",
        "人社局": "https://rsj.sh.gov.cn/"
    },
    "深圳": {
        "人才政策": "https://hrss.sz.gov.cn/",
        "科创委": "https://stic.sz.gov.cn/"
    }
}

def decide_what_to_crawl(user_input):
    """Agent 决策：根据用户指令，决定采集什么"""
    
    # 解析关键词
    if "人才" in user_input or "政策" in user_input:
        return {
            "action": "crawl",
            "source": "人才政策",
            "keywords": ["人才引进", "政策", "申请条件"]
        }
    elif "新闻" in user_input:
        return {"action": "crawl", "source": "新闻", "keywords": ["最新", "动态"]}
    elif "留学" in user_input:
        return {"action": "crawl", "source": "教育", "keywords": ["留学", "大学", "申请"]}
    else:
        return {"action": "crawl", "source": "默认", "keywords": ["资讯"]}

def crawl_url(url, keyword=None):
    """执行爬取"""
    import requests
    from bs4 import BeautifulSoup
    
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text()
        # 提取包含关键词的段落
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if keyword:
            lines = [l for l in lines if keyword in l]
        return lines[:20]  # 返回前20条
    except Exception as e:
        return [f"采集失败: {e}"]

def execute(user_input, location="香港"):
    """执行采集任务"""
    # 1. Agent 决策
    plan = decide_what_to_crawl(user_input)
    print(f"🤖 决策: 采集 {plan['source']} - 关键词 {plan['keywords']}")
    
    # 2. 获取采集源 URL
    source_url = SOURCES.get(location, {}).get(plan['source'])
    if not source_url:
        return {"error": f"未找到 {location} 的 {plan['source']} 采集源"}
    
    # 3. 执行爬取
    print(f"🕷️ 爬取: {source_url}")
    results = crawl_url(source_url, plan['keywords'][0])
    
    return {"source": plan['source'], "url": source_url, "data": results[:10]}

if __name__ == "__main__":
    import sys
    user_input = sys.argv[1] if len(sys.argv) > 1 else "采集香港人才政策"
    result = execute(user_input, "香港")
    print(json.dumps(result, ensure_ascii=False, indent=2))
