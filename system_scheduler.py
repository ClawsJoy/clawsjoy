#!/usr/bin/env python3
"""系统级自动化任务调度器"""

import requests
import subprocess
from pathlib import Path
from datetime import datetime

class SystemScheduler:
    def __init__(self):
        self.log_file = Path("/mnt/d/clawsjoy/logs/system.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {msg}\n")
        print(f"[{timestamp}] {msg}")
    
    def run_health_check(self):
        self.log("🩺 开始健康检查...")
        
        # Chat API
        try:
            resp = requests.post("http://localhost:18109/api/agent", json={"text": "ping"}, timeout=10)
            chat_status = "✅" if resp.status_code == 200 else f"❌ ({resp.status_code})"
        except Exception as e:
            chat_status = f"❌ ({str(e)[:20]})"
        
        # Promo API
        try:
            resp = requests.post("http://localhost:8108/api/promo/make", json={"city": "test"}, timeout=10)
            promo_status = "✅" if resp.status_code == 200 else f"❌ ({resp.status_code})"
        except Exception as e:
            promo_status = f"❌ ({str(e)[:20]})"
        
        # Web
        try:
            resp = requests.get("http://localhost:18083/", timeout=10)
            web_status = "✅" if resp.status_code == 200 else f"❌ ({resp.status_code})"
        except Exception as e:
            web_status = f"❌ ({str(e)[:20]})"
        
        self.log(f"  Chat API: {chat_status}")
        self.log(f"  Promo API: {promo_status}")
        self.log(f"  Web: {web_status}")
    
    def run_url_discovery(self):
        self.log("🔍 开始 URL 发现...")
        try:
            from agents.url_scout import URLScout
            scout = URLScout()
            seeds = ["https://www.immd.gov.hk/hks/", "https://www.info.gov.hk/gia/general/today.htm"]
            total = 0
            for seed in seeds:
                new = scout.discover_from_seed(seed)
                total += len(new)
            self.log(f"✅ URL 发现完成: {total} 个新链接")
        except Exception as e:
            self.log(f"❌ URL 发现失败: {e}")
    
    def run_keyword_learning(self):
        self.log("📚 开始关键词学习...")
        try:
            from agents.keyword_learner import KeywordLearner
            learner = KeywordLearner()
            learned = learner.auto_learn()
            self.log(f"✅ 关键词学习: {len(learned)} 个新词")
        except Exception as e:
            self.log(f"❌ 关键词学习失败: {e}")
    
    def run_cleanup(self):
        self.log("🧹 开始清理临时文件...")
        subprocess.run("rm -f /mnt/d/clawsjoy/web/audio/tts_*.mp3 2>/dev/null", shell=True)
        subprocess.run("rm -f /tmp/tts_*.mp3 /tmp/mixed_*.mp3 2>/dev/null", shell=True)
        self.log("✅ 临时文件清理完成")
    
    def run_all(self):
        self.log("=" * 50)
        self.log("🚀 执行系统任务")
        self.run_url_discovery()
        self.run_keyword_learning()
        self.run_cleanup()
        self.run_health_check()
        self.log("✅ 系统任务完成")
        self.log("=" * 50)

if __name__ == "__main__":
    import sys
    scheduler = SystemScheduler()
    if len(sys.argv) > 1:
        task = sys.argv[1]
        if task == "health":
            scheduler.run_health_check()
        elif task == "url":
            scheduler.run_url_discovery()
        elif task == "keyword":
            scheduler.run_keyword_learning()
        elif task == "clean":
            scheduler.run_cleanup()
        else:
            scheduler.run_all()
    else:
        scheduler.run_all()
