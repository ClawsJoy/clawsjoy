#!/usr/bin/env python3
"""剧集管理系统 - 避免内容重复"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

SERIES_DIR = Path("/mnt/d/clawsjoy/series/hk_immigration")
EPISODE_LOG = SERIES_DIR / "episodes.json"

def load_episodes():
    """加载已有剧集"""
    if EPISODE_LOG.exists():
        with open(EPISODE_LOG, 'r') as f:
            return json.load(f)
    return []

def save_episode(episode):
    """保存剧集记录"""
    episodes = load_episodes()
    episodes.append(episode)
    with open(EPISODE_LOG, 'w') as f:
        json.dump(episodes[-100:], f, ensure_ascii=False, indent=2)  # 保留最近100集

def get_content_hash(content):
    """计算内容哈希用于去重"""
    return hashlib.md5(content.encode()).hexdigest()[:8]

def is_duplicate(new_content, threshold=0.7):
    """检查是否与已有内容重复"""
    episodes = load_episodes()
    if not episodes:
        return False
    
    new_hash = get_content_hash(new_content[:500])  # 只检查前500字
    
    for ep in episodes[-20:]:  # 检查最近20集
        if ep.get("content_hash") == new_hash:
            return True
        
        # 简单关键词重叠检查
        new_keywords = set(new_content[:200].split(' '))
        old_keywords = set(ep.get("preview", "")[:200].split(' '))
        overlap = len(new_keywords & old_keywords) / max(len(new_keywords), 1)
        if overlap > threshold:
            return True
    
    return False

def get_next_episode():
    """获取下一集编号"""
    episodes = load_episodes()
    return len(episodes) + 1

def generate_unique_content(topic, context, avoid_topics=[]):
    """生成不重复的内容"""
    import requests
    
    avoid_str = "，避免以下内容：" + "、".join(avoid_topics[-5:]) if avoid_topics else ""
    
    prompt = f"""请为「{topic}」写一篇新的解说词，用于第{get_next_episode()}集。
{avoid_str}

【资料】
{chr(10).join(context)[:3000]}

【要求】
- 选择与以前不同的角度
- 每个都是新的内容，不要重复
- 纯文本，无标记
- 字数：1000-1500字
- 直接输出："""

    resp = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "options": {"num_predict": 2500}
    }, timeout=120)
    
    if resp.status_code == 200:
        return resp.json().get("response", "")
    return ""

if __name__ == "__main__":
    # 显示已有剧集
    episodes = load_episodes()
    print(f"📺 已有 {len(episodes)} 集")
    for ep in episodes[-5:]:
        print(f"  第{ep['number']}集: {ep['topic'][:30]}...")
