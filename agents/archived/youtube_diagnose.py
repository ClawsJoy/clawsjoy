#!/usr/bin/env python3
"""YouTube 频道诊断 - 简洁版"""

import pickle
from pathlib import Path
from googleapiclient.discovery import build

TOKEN_FILE = Path("/mnt/d/clawsjoy/config/youtube/token.pickle")

def main():
    # 加载令牌
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    
    print(f"令牌有效: {not creds.expired}")
    print(f"权限范围: {creds.scopes}")
    
    # 构建服务
    youtube = build('youtube', 'v3', credentials=creds)
    
    # 获取频道信息
    try:
        channel = youtube.channels().list(part='statistics', mine=True).execute()
        if channel['items']:
            stats = channel['items'][0]['statistics']
            print(f"\n📊 频道统计:")
            print(f"  订阅者: {stats.get('subscriberCount', 0)}")
            print(f"  总观看: {stats.get('viewCount', 0)}")
            print(f"  视频数: {stats.get('videoCount', 0)}")
        else:
            print("未找到频道")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
