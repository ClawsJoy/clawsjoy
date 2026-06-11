#!/usr/bin/env python3
"""自动生成推广内容"""

import requests
import json
from datetime import datetime


def generate_article(topic: str) -> str:
    """调用LLM生成技术文章"""
    prompt = f"""
请写一篇关于 ClawsJoy 的技术文章，主题是：{topic}

要求：
1. 标题吸引人
2. 开头引人入胜
3. 有代码示例
4. 有使用场景
5. 结尾有号召

文章长度：800-1000字
"""
    
    try:
        resp = requests.post(
            "http://localhost:5012/chat",
            json={"message": prompt},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except:
        pass
    return ""


def generate_tweet(feature: str) -> str:
    """生成推广推文"""
    prompt = f"""
请为 ClawsJoy 的 {feature} 功能写一条推广推文（<200字）：
- 突出亮点
- 添加相关话题标签
- 语气热情
"""
    try:
        resp = requests.post(
            "http://localhost:5012/chat",
            json={"message": prompt},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except:
        pass
    return ""


if __name__ == "__main__":
    topics = [
        "企业级AI助手的本地化部署",
        "零成本构建企业内部智能助手",
        "数据隐私时代的AI解决方案",
        "开源AI助手对比：为什么选择ClawsJoy"
    ]
    
    for topic in topics:
        print(f"\n生成文章: {topic}")
        article = generate_article(topic)
        print(article[:200] + "...")
        print("-" * 50)
