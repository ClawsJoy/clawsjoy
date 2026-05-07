#!/usr/bin/env python3
"""专业工程师 Agent - 从知识库学习"""

import json
import subprocess
from pathlib import Path

class ProfessionalEngineer:
    def __init__(self):
        self.knowledge_base = Path("/mnt/d/clawsjoy/knowledge")
        self.learned_file = Path("/mnt/d/clawsjoy/data/engineer_knowledge.json")
        self.competency = {
            "systemd": 0,
            "pm2": 0,
            "python_path": 0,
            "docker": 0,
            "network": 0,
            "clawsjoy": 0
        }
        self.load()
    
    def load(self):
        if self.learned_file.exists():
            with open(self.learned_file) as f:
                data = json.load(f)
                self.competency = data.get("competency", self.competency)
    
    def save(self):
        with open(self.learned_file, 'w') as f:
            json.dump({
                "competency": self.competency,
                "last_learned": __import__('time').time(),
                "knowledge_areas": list(self.competency.keys())
            }, f, indent=2)
    
    def learn_from_file(self, filepath, topic):
        """从文件学习知识"""
        if not filepath.exists():
            return
        
        with open(filepath) as f:
            content = f.read()
        
        # 学习成果：提取关键命令和概念
        learned = {
            "topic": topic,
            "file": str(filepath),
            "size": len(content),
            "key_concepts": self._extract_concepts(content)
        }
        
        # 更新能力值
        self.competency[topic] = min(100, self.competency.get(topic, 0) + 15)
        self.save()
        
        print(f"📚 工程师学习了 [{topic}]: {self.competency[topic]}%")
        return learned
    
    def _extract_concepts(self, content):
        """提取关键概念"""
        concepts = []
        keywords = ["命令", "问题", "方案", "配置", "排查", "修复"]
        for line in content.split('\n'):
            for kw in keywords:
                if kw in line and len(line) < 100:
                    concepts.append(line.strip()[:50])
                    break
        return concepts[:10]
    
    def learn_all(self):
        """学习所有知识"""
        print("🧠 工程师 Agent 开始学习...")
        
        learnings = []
        
        # 学习各领域知识
        topics = {
            "systemd": "systemd/service_management.md",
            "pm2": "pm2/advanced.md",
            "python_path": "python/module_paths.md",
            "docker": "docker/operations.md",
            "network": "network/troubleshooting.md",
            "clawsjoy": "clawsjoy/architecture.md"
        }
        
        for topic, rel_path in topics.items():
            filepath = self.knowledge_base / rel_path
            if filepath.exists():
                learning = self.learn_from_file(filepath, topic)
                learnings.append(learning)
            else:
                print(f"⚠️ 未找到知识文件: {rel_path}")
        
        return learnings
    
    def can_fix(self, problem):
        """判断是否能修复该问题"""
        problem_lower = problem.lower()
        
        fixes = []
        
        if "module" in problem_lower and "not found" in problem_lower:
            fixes.append("检查 Python 导入路径")
            fixes.append("添加 sys.path.insert(0, '/mnt/d/clawsjoy')")
        
        if "address already in use" in problem_lower:
            fixes.append("释放端口: sudo fuser -k <port>/tcp")
        
        if "connection refused" in problem_lower:
            fixes.append("检查服务是否启动: pm2 list")
        
        if "docker" in problem_lower and "socket" in problem_lower:
            fixes.append("启动 Docker: sudo service docker start")
        
        return fixes
    
    def get_advice(self, symptom):
        """根据症状提供专业建议"""
        advice = self.can_fix(symptom)
        if advice:
            return {
                "symptom": symptom,
                "diagnosis": "根据专业知识分析",
                "solutions": advice,
                "confidence": self.competency.get("clawsjoy", 50)
            }
        return {"symptom": symptom, "advice": "需要进一步学习"}

if __name__ == "__main__":
    engineer = ProfessionalEngineer()
    
    # 学习
    engineer.learn_all()
    
    # 显示学习成果
    print("\n📊 工程师能力评估:")
    for area, level in engineer.competency.items():
        bar = "█" * (level // 10) + "░" * (10 - level // 10)
        print(f"  {area:12}: [{bar}] {level}%")
    
    # 测试诊断
    print("\n🔧 诊断测试:")
    test_problems = [
        "ModuleNotFoundError: No module named 'keyword_learner'",
        "Address already in use on port 18103",
        "docker.sock: connect: no such file or directory"
    ]
    
    for problem in test_problems:
        advice = engineer.get_advice(problem)
        print(f"\n  问题: {problem[:50]}...")
        if advice.get("solutions"):
            print(f"  方案: {advice['solutions']}")
        else:
            print(f"  建议: {advice.get('advice', '未知')}")

    def reload_from_crawled(self):
        """从采集的知识库重新加载"""
        crawled_dir = self.knowledge_base / "collected"
        if not crawled_dir.exists():
            return
        
        print("📚 加载采集的知识...")
        loaded = 0
        for file in crawled_dir.glob("*.md"):
            with open(file) as f:
                content = f.read()
            
            # 提取有用信息
            topic = file.stem
            if "command" in content:
                self.competency[topic] = min(100, self.competency.get(topic, 0) + 20)
                loaded += 1
        
        if loaded:
            self.save()
            print(f"✅ 加载了 {loaded} 个知识源")
        
        return loaded
