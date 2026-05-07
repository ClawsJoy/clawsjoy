#!/usr/bin/env python3
"""学习型 Agent - 具备知识库和自我学习能力"""

import json
import re
import subprocess
from pathlib import Path
from datetime import datetime

class LearningAgent:
    def __init__(self):
        self.knowledge_dir = Path("/mnt/d/clawsjoy/data/knowledge")
        self.learned_file = self.knowledge_dir / "learned.json"
        self.load_learned()
    
    def load_learned(self):
        if self.learned_file.exists():
            with open(self.learned_file) as f:
                self.learned = json.load(f)
        else:
            self.learned = {"fixes": [], "patterns": [], "stats": {}}
    
    def save_learned(self):
        with open(self.learned_file, 'w') as f:
            json.dump(self.learned, f, indent=2)
    
    def learn_from_error(self, error_text, context=None):
        """从错误中学习"""
        # 提取错误模式
        patterns = {
            "port_conflict": r"Address already in use.*:(\d+)",
            "connection_refused": r"Connection refused.*:(\d+)",
            "timeout": r"timed out|timeout",
            "no_such_host": r"No such host",
            "permission_denied": r"Permission denied|Operation not permitted"
        }
        
        learned_pattern = None
        for name, pattern in patterns.items():
            match = re.search(pattern, error_text, re.IGNORECASE)
            if match:
                learned_pattern = {
                    "type": name,
                    "error": error_text[:200],
                    "context": context,
                    "learned_at": datetime.now().isoformat(),
                    "port": match.group(1) if match.groups() else None
                }
                break
        
        if learned_pattern:
            # 检查是否已学习过
            exists = False
            for p in self.learned["patterns"]:
                if p["type"] == learned_pattern["type"]:
                    exists = True
                    break
            if not exists:
                self.learned["patterns"].append(learned_pattern)
                self.save_learned()
                print(f"📚 学习了新模式: {learned_pattern['type']}")
                return learned_pattern
        return None
    
    def get_fix_suggestion(self, error_text):
        """根据错误建议修复方案"""
        suggestions = []
        
        # 端口冲突
        if "Address already in use" in error_text:
            port_match = re.search(r':(\d+)', error_text)
            port = port_match.group(1) if port_match else "unknown"
            suggestions.append({
                "action": f"sudo fuser -k {port}/tcp",
                "description": f"释放端口 {port}"
            })
            suggestions.append({
                "action": "pm2 restart all",
                "description": "重启所有服务"
            })
        
        # 连接拒绝
        if "Connection refused" in error_text:
            suggestions.append({
                "action": "cd /mnt/d/clawsjoy && ./start.sh",
                "description": "重新启动所有服务"
            })
            suggestions.append({
                "action": "pm2 restart chat-api",
                "description": "重启 Chat API"
            })
        
        # 权限问题
        if "Permission denied" in error_text or "Operation not permitted" in error_text:
            suggestions.append({
                "action": "sudo chown -R flybo:flybo /mnt/d/clawsjoy",
                "description": "修复文件权限"
            })
        
        return suggestions
    
    def learn_network_troubleshooting(self):
        """学习网络排障知识"""
        network_knowledge = {
            "诊断步骤": [
                "1. 检查端口监听: ss -tlnp | grep {port}",
                "2. 检查进程: ps aux | grep {service}",
                "3. 检查日志: tail -50 logs/{service}.log",
                "4. 测试连通性: curl -v http://localhost:{port}"
            ],
            "常用命令": {
                "查看端口": "sudo lsof -i :{port}",
                "查看进程树": "pstree -p {pid}",
                "查看网络连接": "netstat -an | grep {port}"
            }
        }
        
        knowledge_file = self.knowledge_dir / "networking/troubleshooting.json"
        with open(knowledge_file, 'w') as f:
            json.dump(network_knowledge, f, indent=2)
        
        print("📚 学习了网络排障知识")
        return network_knowledge
    
    def learn_system_maintenance(self):
        """学习系统维护知识"""
        system_knowledge = {
            "日常检查": [
                "磁盘使用: df -h",
                "内存使用: free -h",
                "CPU负载: top -bn1 | head -5",
                "服务状态: pm2 list",
                "容器状态: docker ps"
            ],
            "性能优化": [
                "清理日志: find logs -name '*.log' -size +50M -delete",
                "清理缓存: docker system prune -f",
                "重启服务: pm2 restart all"
            ]
        }
        
        knowledge_file = self.knowledge_dir / "system/maintenance.json"
        with open(knowledge_file, 'w') as f:
            json.dump(system_knowledge, f, indent=2)
        
        print("📚 学习了系统维护知识")
        return system_knowledge

if __name__ == "__main__":
    agent = LearningAgent()
    print("=== 学习型 Agent ===")
    agent.learn_network_troubleshooting()
    agent.learn_system_maintenance()
    
    # 模拟学习错误
    test_error = "Address already in use on port 8108"
    learned = agent.learn_from_error(test_error)
    print(f"从错误中学习: {learned}")
    
    # 获取修复建议
    suggestions = agent.get_fix_suggestion(test_error)
    print(f"修复建议: {suggestions}")
