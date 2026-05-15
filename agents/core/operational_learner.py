#!/usr/bin/env python3
"""从系统运营过程中学习的 Agent"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

class OperationalLearner:
    def __init__(self):
        self.learning_dir = Path("/mnt/d/clawsjoy/data/learning")
        self.learning_dir.mkdir(parents=True, exist_ok=True)
    
    def learn_from_logs(self):
        """从日志中学习用户指令"""
        # 查找正确的日志文件
        log_files = [
            Path("/mnt/d/clawsjoy/logs/chat-api-out.log"),
            Path("/mnt/d/clawsjoy/logs/chat-api.log"),
            Path("/tmp/chat-api-out.log")
        ]
        
        log_content = ""
        for log_file in log_files:
            if log_file.exists():
                with open(log_file) as f:
                    log_content = f.read()
                break
        
        if not log_content:
            print("⚠️ 未找到日志文件")
            return
        
        commands = re.findall(r'📥 处理: (.*?)[\n\.]', log_content)
        if commands:
            freq = Counter(commands[-50:])
            print(f"📊 学习到高频指令: {dict(freq.most_common(3))}")
            
            with open(self.learning_dir / "learned_commands.json", 'w') as f:
                json.dump(dict(freq.most_common(10)), f, ensure_ascii=False, indent=2)
    
    def learn_from_errors(self):
        """从错误中学习"""
        error_files = [
            Path("/mnt/d/clawsjoy/logs/engineer.log"),
            Path("/mnt/d/clawsjoy/logs/system.log")
        ]
        
        errors = ""
        for ef in error_files:
            if ef.exists():
                with open(ef) as f:
                    errors += f.read()
        
        if not errors:
            return
        
        patterns = re.findall(r'❌ (.*?)(?:\n|$)', errors)
        if patterns:
            freq = Counter(patterns[-30:])
            print(f"🔧 学习到高频错误: {dict(freq.most_common(3))}")
            
            with open(self.learning_dir / "learned_errors.json", 'w') as f:
                json.dump(dict(freq.most_common(5)), f, ensure_ascii=False, indent=2)
    
    def learn_from_results(self):
        """从执行结果中学习"""
        video_dir = Path("/mnt/d/clawsjoy/web/videos")
        if not video_dir.exists():
            return
        
        videos = list(video_dir.glob("*.mp4"))
        if videos:
            sizes = [v.stat().st_size for v in videos[-10:]]
            avg_size = sum(sizes) / len(sizes) if sizes else 0
            print(f"🎬 学习到视频平均大小: {avg_size/1024/1024:.1f} MB")
            
            with open(self.learning_dir / "learned_videos.json", 'w') as f:
                json.dump({
                    "count": len(videos),
                    "avg_size_mb": avg_size/1024/1024,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)
    
    def learn_all(self):
        print("🧠 开始从运营过程中学习...")
        self.learn_from_logs()
        self.learn_from_errors()
        self.learn_from_results()
        print("✅ 学习完成")

if __name__ == "__main__":
    learner = OperationalLearner()
    learner.learn_all()
