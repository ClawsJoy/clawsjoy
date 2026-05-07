#!/usr/bin/env python3
"""工程师 Agent 专属学习 - 系统运维知识"""

import subprocess
import json
import re
from base_learner import BaseLearner

class EngineerLearner(BaseLearner):
    def __init__(self):
        super().__init__("engineer_agent", "engineering")
    
    def learn(self, new_knowledge=None):
        """学习系统运维知识"""
        knowledge = []
        
        # 1. 学习端口模式
        ports_output = subprocess.check_output("ss -tlnp", shell=True).decode()
        port_patterns = re.findall(r':(\d+).*?\((.*?)\)', ports_output)
        for port, proc in port_patterns[:10]:
            knowledge.append({
                "type": "port_usage",
                "port": port,
                "process": proc.strip(),
                "learned_at": __import__('time').time()
            })
        
        # 2. 学习服务依赖
        services = subprocess.check_output("pm2 list", shell=True).decode()
        for line in services.split('\n'):
            if 'online' in line or 'errored' in line:
                parts = line.split('│')
                if len(parts) > 2:
                    knowledge.append({
                        "type": "service_status",
                        "name": parts[1].strip(),
                        "status": parts[6].strip() if len(parts) > 6 else "unknown"
                    })
        
        self.learned["knowledge"] = knowledge[-50:]  # 保留最近50条
        self.save_learned()
        return knowledge
    
    def get_fix_suggestion(self, error):
        """根据错误提供修复建议"""
        suggestions = []
        
        # 端口冲突
        port_match = re.search(r'port\s*(\d+)|:(\d+)', error)
        if port_match:
            port = port_match.group(1) or port_match.group(2)
            suggestions.append(f"fuser -k {port}/tcp")
            suggestions.append("pm2 restart all")
        
        # 服务异常
        if "errored" in error or "failed" in error:
            suggestions.append("pm2 restart {service}")
            suggestions.append("pm2 logs {service} --lines 20")
        
        # 磁盘空间
        if "space" in error.lower():
            suggestions.append("python3 agents/cleaner_agent.py smart")
        
        return suggestions

# 测试
if __name__ == "__main__":
    learner = EngineerLearner()
    learned = learner.learn()
    print(f"学习了 {len(learned)} 条运维知识")
    print(f"统计: {learner.get_stats()}")
