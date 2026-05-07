#!/usr/bin/env python3
"""YouTube 评论安全回复器"""

import json
import re
import time
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# 加载安全规则
with open('/mnt/d/clawsjoy/config/youtube_safety_rules.json', 'r') as f:
    SAFETY_RULES = json.load(f)

def filter_sensitive_content(text):
    """过滤敏感内容"""
    for keyword in SAFETY_RULES['禁止内容']:
        if keyword in text:
            return True, keyword
    return False, None

def validate_reply(reply_text):
    """验证回复是否合规"""
    # 检查是否包含禁止回复语
    for forbidden in SAFETY_RULES['禁止回复']:
        if forbidden in reply_text:
            return False, f"包含禁止词: {forbidden}"
    
    # 检查长度
    if len(reply_text) > 200:
        return False, "回复过长"
    
    if len(reply_text) < 5:
        return False, "回复过短"
    
    return True, "ok"

def generate_safe_reply(comment_text):
    """生成安全回复"""
    import requests
    
    # 先过滤评论
    has_sensitive, keyword = filter_sensitive_content(comment_text)
    if has_sensitive:
        return None, f"检测到敏感词: {keyword}"
    
    # 限制回复长度
    prompt = f"""你是一个专业的香港签证频道博主。请友好回复以下评论。

规则：
1. 回复精简，30字以内
2. 不承诺保证
3. 可引导关注频道
4. 不讨论政治
5. 不说"我是AI"

评论：{comment_text}

回复："""
    
    try:
        resp = requests.post("http://localhost:8101/api/agent",
            json={"text": prompt}, timeout=30)
        if resp.status_code == 200:
            reply = resp.json().get('message', '感谢支持！')
            # 验证回复
            valid, reason = validate_reply(reply)
            if valid:
                return reply, "ok"
            else:
                return "感谢你的评论！我们会持续分享香港资讯。", f"原回复不合规: {reason}"
    except:
        pass
    
    return "感谢你的支持！欢迎持续关注。", "使用默认回复"

def auto_reply_safe():
    """安全自动回复"""
    from youtube_comments import get_latest_comments, reply_to_comment, load_replied_ids, save_replied_id
    
    comments = get_latest_comments(10)
    replied_ids = load_replied_ids()
    
    daily_count = 0
    for comment in comments:
        if comment['id'] in replied_ids:
            continue
        
        # 每日上限检查
        if daily_count >= SAFETY_RULES['每日回复上限']:
            print("⚠️ 已达每日回复上限")
            break
        
        # 敏感词过滤
        has_sensitive, keyword = filter_sensitive_content(comment['text'])
        if has_sensitive:
            print(f"⚠️ 跳过敏感评论: {keyword}")
            save_replied_id(comment['id'])  # 标记已处理但不回复
            continue
        
        # 生成回复
        reply, status = generate_safe_reply(comment['text'])
        if reply:
            if reply_to_comment(comment['id'], reply):
                save_replied_id(comment['id'])
                daily_count += 1
                print(f"✅ 回复: {reply[:30]}...")
        
        time.sleep(5)
    
    print(f"📊 今日回复: {daily_count} 条")

if __name__ == "__main__":
    auto_reply_safe()
