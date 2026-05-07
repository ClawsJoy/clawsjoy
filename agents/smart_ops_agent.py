#!/usr/bin/env python3
"""智能运维 Agent - 真正学习的 Agent"""

import subprocess
import json
import re
import time
from pathlib import Path
from datetime import datetime

class SmartOpsAgent:
    def __init__(self):
        self.memory_file = Path("/mnt/d/clawsjoy/data/ops_memory.json")
        self.load_memory()
    
    def load_memory(self):
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                self.memory = json.load(f)
        else:
            self.memory = {
                "experiences": [],
                "skills_performance": {},
                "learned_patterns": []
            }
    
    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def get_state(self):
        state = {}
        result = subprocess.run("pm2 list", shell=True, capture_output=True, text=True)
        output = result.stdout
        
        for svc in ["agent-api", "chat-api", "promo-api"]:
            if svc in output:
                if "errored" in output:
                    state[svc] = "errored"
                elif "online" in output:
                    state[svc] = "online"
                else:
                    state[svc] = "unknown"
            else:
                state[svc] = "not_found"
        
        result = subprocess.run("docker ps", shell=True, capture_output=True, text=True)
        state["web"] = "running" if "clawsjoy-web" in result.stdout else "stopped"
        
        return state
    
    def get_action(self, problem):
        rules = {
            "agent-api": {
                "cmd": "cd /mnt/d/clawsjoy/bin && pm2 start agent_api.py --name agent-api -- --port 18103 2>/dev/null || pm2 restart agent-api",
                "verify": "pm2 list | grep agent-api | grep -q online"
            },
            "chat-api": {
                "cmd": "cd /mnt/d/clawsjoy/bin && pm2 start chat_api.py --name chat-api -- --port 18109 2>/dev/null || pm2 restart chat-api",
                "verify": "pm2 list | grep chat-api | grep -q online"
            },
            "promo-api": {
                "cmd": "cd /mnt/d/clawsjoy/bin && pm2 start promo_api.py --name promo-api -- --port 8108 2>/dev/null || pm2 restart promo-api",
                "verify": "pm2 list | grep promo-api | grep -q online"
            },
            "web": {
                "cmd": "cd /mnt/d/clawsjoy && docker-compose up -d web 2>/dev/null || docker start clawsjoy-web",
                "verify": "docker ps | grep -q clawsjoy-web"
            }
        }
        
        for svc, info in rules.items():
            if svc in problem:
                return info
        return None
    
    def execute(self, action, problem):
        print(f"执行修复: {problem}")
        subprocess.run(action["cmd"], shell=True, capture_output=True)
        time.sleep(2)
        verify = subprocess.run(action["verify"], shell=True)
        success = verify.returncode == 0
        return success
    
    def learn(self, problem, success):
        action_name = problem.split(".")[0] if "." in problem else problem
        if action_name not in self.memory["skills_performance"]:
            self.memory["skills_performance"][action_name] = {"total": 0, "success": 0}
        
        self.memory["skills_performance"][action_name]["total"] += 1
        if success:
            self.memory["skills_performance"][action_name]["success"] += 1
        
        self.memory["experiences"].append({
            "time": datetime.now().isoformat(),
            "problem": problem,
            "success": success
        })
        
        self.save_memory()
    
    def auto_heal(self):
        print("智能运维 Agent 启动...")
        state = self.get_state()
        
        problems = []
        for svc, status in state.items():
            if status in ["errored", "not_found", "stopped"]:
                problems.append(f"{svc}.{status}")
        
        if not problems:
            print("所有服务正常")
            return
        
        for problem in problems:
            action = self.get_action(problem)
            if action:
                success = self.execute(action, problem)
                self.learn(problem, success)
                print(f"{problem}: {'成功' if success else '失败'}")
            else:
                print(f"未找到 {problem} 的修复方案")
        
        print("\n学习统计:")
        for skill, stats in self.memory["skills_performance"].items():
            rate = stats["success"] / max(stats["total"], 1) * 100
            print(f"  {skill}: {stats['success']}/{stats['total']} ({rate:.0f}%)")

if __name__ == "__main__":
    agent = SmartOpsAgent()
    agent.auto_heal()
