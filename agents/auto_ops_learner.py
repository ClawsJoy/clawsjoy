#!/usr/bin/env python3
"""自主运维学习器 - 让 Agent 学会维护系统"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

class AutoOpsLearner:
    def __init__(self):
        self.knowledge_file = Path("/mnt/d/clawsjoy/data/ops_knowledge.json")
        self.load_knowledge()
    
    def load_knowledge(self):
        if self.knowledge_file.exists():
            with open(self.knowledge_file) as f:
                self.knowledge = json.load(f)
        else:
            self.knowledge = {
                "learned_fixes": [],
                "service_patterns": {},
                "last_learned": None
            }
    
    def save_knowledge(self):
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def learn_service_recovery(self):
        """学习服务恢复"""
        services = {
            "agent-api": {"script": "agent_api.py", "port": 18103},
            "chat-api": {"script": "chat_api.py", "port": 18109},
            "promo-api": {"script": "promo_api.py", "port": 8108},
            "health-api": {"script": "health_api.py", "port": 18110}
        }
        
        for name, info in services.items():
            # 检查服务状态
            result = subprocess.run(f"pm2 list | grep {name} | grep -q online", shell=True)
            
            if result.returncode != 0:
                print(f"🔧 学习修复: {name} 服务异常")
                
                # 尝试重启
                subprocess.run(f"cd /mnt/d/clawsjoy/bin && pm2 start {info['script']} --interpreter python3 --name {name} -- --port {info['port']}", shell=True)
                
                # 记录学到的知识
                fix = {
                    "problem": f"{name} service stopped",
                    "solution": f"pm2 start {info['script']} --name {name} -- --port {info['port']}",
                    "learned_at": datetime.now().isoformat(),
                    "success": True
                }
                
                # 避免重复记录
                if not any(f["problem"] == fix["problem"] for f in self.knowledge["learned_fixes"]):
                    self.knowledge["learned_fixes"].append(fix)
                    self.save_knowledge()
                    print(f"📚 Agent 学会了修复 {name}")
    
    def learn_from_errors(self):
        """从错误中学习"""
        log_file = Path("/mnt/d/clawsjoy/logs/system.log")
        if not log_file.exists():
            return
        
        with open(log_file) as f:
            logs = f.read()
        
        # 提取错误模式及解决方案
        error_solutions = {
            "ModuleNotFoundError": "pip install -r requirements.txt",
            "Address already in use": "sudo fuser -k {port}/tcp",
            "Connection refused": "pm2 restart {service}",
            "TimeoutError": "增加超时时间配置",
            "Permission denied": "sudo chown -R flybo:flybo /mnt/d/clawsjoy"
        }
        
        learned = []
        for error, solution in error_solutions.items():
            if error in logs:
                learned.append({"error": error, "solution": solution})
        
        if learned:
            for l in learned:
                if not any(f.get("error") == l["error"] for f in self.knowledge["learned_fixes"]):
                    self.knowledge["learned_fixes"].append(l)
            self.save_knowledge()
            print(f"📚 Agent 学会了 {len(learned)} 个错误修复方案")
    
    def apply_learned_fixes(self):
        """应用学到的修复方案"""
        for fix in self.knowledge["learned_fixes"]:
            if "solution" in fix:
                print(f"🔧 应用修复: {fix.get('problem', fix.get('error', 'unknown'))}")
                subprocess.run(fix["solution"], shell=True)
    
    def auto_heal(self):
        """自动治愈"""
        print("🩺 Agent 开始自主运维...")
        self.learn_service_recovery()
        self.learn_from_errors()
        self.apply_learned_fixes()
        print("✅ 自主运维完成")

if __name__ == "__main__":
    learner = AutoOpsLearner()
    learner.auto_heal()
    
    # 显示学到的知识
    print("\n📚 Agent 已学会的知识:")
    for fix in learner.knowledge.get("learned_fixes", [])[-5:]:
        print(f"  - {fix.get('problem', fix.get('error', '?'))}")
