#!/usr/bin/env python3
"""专业学习 Agent - 从文档和实践中学习"""

import subprocess
import json
from pathlib import Path

class ProfessionalLearner:
    def __init__(self):
        self.knowledge_base = Path("/mnt/d/clawsjoy/knowledge")
        self.learned = Path("/mnt/d/clawsjoy/data/professional_knowledge.json")
        self.load()
    
    def load(self):
        if self.learned.exists():
            with open(self.learned) as f:
                self.data = json.load(f)
        else:
            self.data = {"learned": []}
    
    def save(self):
        with open(self.learned, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def learn_from_docs(self):
        """从文档学习"""
        for doc_file in self.knowledge_base.rglob("*.md"):
            with open(doc_file) as f:
                content = f.read()
            
            # 提取关键知识点
            topics = []
            if "服务管理" in content:
                topics.append("service_management")
            if "Python 导入" in content:
                topics.append("python_import")
            if "Docker" in content:
                topics.append("docker_ops")
            
            for topic in topics:
                if topic not in self.data["learned"]:
                    self.data["learned"].append(topic)
                    print(f"📚 学习了: {topic}")
        
        self.save()
    
    def apply_knowledge(self, problem):
        """应用学到的知识解决问题"""
        if "ModuleNotFoundError" in problem:
            print("🔧 应用知识: 修复 Python 导入路径")
            return "sed -i 's/from keyword_learner/from agents.keyword_learner/g' agents/tenant_agent.py"
        
        if "Address already in use" in problem:
            print("🔧 应用知识: 释放端口")
            return "sudo fuser -k 18103/tcp"
        
        if "docker.sock" in problem:
            print("🔧 应用知识: 启动 Docker")
            return "sudo service docker start"
        
        return None
    
    def auto_fix_by_knowledge(self):
        """根据学到的知识自动修复"""
        print("🧠 根据专业知识自动修复...")
        
        # 修复 agent-api 导入问题
        fix_cmd = self.apply_knowledge("ModuleNotFoundError")
        if fix_cmd:
            subprocess.run(fix_cmd, shell=True)
            subprocess.run("pm2 restart agent-api", shell=True)
            print("✅ 已应用知识修复")
        
        # 修复 Docker
        fix_cmd = self.apply_knowledge("docker.sock")
        if fix_cmd:
            subprocess.run(fix_cmd, shell=True)

if __name__ == "__main__":
    learner = ProfessionalLearner()
    learner.learn_from_docs()
    learner.auto_fix_by_knowledge()
