#!/usr/bin/env python3
"""运维管家 - 整合 all agent 能力"""

import subprocess
import requests
import json
import time
from pathlib import Path
from datetime import datetime
from engineer_agent import EngineerAgent
from self_healing import SelfHealingAgent
from cleaner_agent import CleanerAgent

class OpsAgent:
    def __init__(self):
        self.engineer = EngineerAgent()
        self.healer = SelfHealingAgent()
        self.cleaner = CleanerAgent()
        self.log_file = Path("/mnt/d/clawsjoy/logs/ops_agent.log")
    
    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {msg}\n")
        print(f"[{timestamp}] {msg}")
    
    def daily_maintenance(self):
        """每日日常维护"""
        self.log("=" * 50)
        self.log("🛠️ 开始每日日常维护")
        
        # 1. 健康检查
        self.log("📊 执行健康检查...")
        self.engineer.check_services()
        
        # 2. 自愈检查
        self.log("🔧 检查自愈需求...")
        # 读取最新错误日志
        error_log = self._get_recent_errors()
        fixes = self.healer.heal(error_log)
        self.log(f"应用了 {len(fixes)} 个修复")
        
        # 3. 清理临时文件
        self.log("🧹 清理临时文件...")
        self.cleaner.scan_disk()
        
        # 4. 备份数据
        self.log("💾 备份数据...")
        subprocess.run("cd /mnt/d/clawsjoy && ./bin/backup.sh", shell=True)
        
        # 5. 日志轮转
        self.log("📝 日志轮转...")
        subprocess.run("cd /mnt/d/clawsjoy && ./bin/log_rotate.sh", shell=True)
        
        self.log("✅ 日常维护完成")
        self.log("=" * 50)
    
    def _get_recent_errors(self):
        """获取最近错误日志"""
        error_log = ""
        log_files = ["logs/monitor.log", "logs/system.log", ".pm2/logs/*-error.log"]
        for pattern in log_files:
            for f in Path("/mnt/d/clawsjoy").glob(pattern):
                if f.exists():
                    with open(f) as fp:
                        lines = fp.readlines()[-50:]
                        error_log += "".join(lines)
        return error_log
    
    def emergency_fix(self):
        """紧急修复"""
        self.log("🚨 执行紧急修复...")
        
        # 重启所有服务
        subprocess.run("cd /mnt/d/clawsjoy && pm2 restart all", shell=True)
        subprocess.run("cd /mnt/d/clawsjoy && docker-compose restart", shell=True)
        
        # 等待服务启动
        time.sleep(5)
        
        # 健康检查
        self.engineer.check_services()
        
        self.log("✅ 紧急修复完成")
    
    def run(self, task="daily"):
        if task == "daily":
            self.daily_maintenance()
        elif task == "emergency":
            self.emergency_fix()
        elif task == "health":
            self.engineer.check_services()
        else:
            self.daily_maintenance()

if __name__ == "__main__":
    import sys
    agent = OpsAgent()
    task = sys.argv[1] if len(sys.argv) > 1 else "daily"
    agent.run(task)
