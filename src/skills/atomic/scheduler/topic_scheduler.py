#!/usr/bin/env python3
"""Topic Scheduler - Topic Scheduler 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import schedule
import time
import threading
from datetime import datetime
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

class TopicScheduler:
    def __init__(self):
        self.running = True
        self.config = {
            "threshold": 3,
            "top_k": 10,
            "retention_days": 30
        }
    
    def start(self):
        # 每30分钟执行一次（测试用）
        schedule.every(30).minutes.do(self.collect)
        schedule.every().day.at("02:00").do(self.cleanup)
        
        print(f"📅 定时任务已启动（每30分钟采集一次）")
        
        def run():
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def collect(self):
        print(f"[{datetime.now()}] 🔥 采集热门话题...")
        try:
            from src.skills.atomic.crawler.hot_topic_crawler import skill
            result = skill.execute({})
            print(f"✅ 采集完成: {result.get('message', '')}")
        except Exception as e:
            print(f"❌ 采集失败: {e}")
    
    def cleanup(self):
        print(f"[{datetime.now()}] 🧹 清理过期数据...")

topic_scheduler = TopicScheduler()
