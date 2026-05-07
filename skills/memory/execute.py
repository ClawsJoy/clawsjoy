#!/usr/bin/env python3
"""ClawsJoy 记忆系统 - 简化版"""

import json
from pathlib import Path
from datetime import datetime

class ClawsJoyMemory:
    def __init__(self, tenant_id="1"):
        self.memory_file = Path(f"/mnt/d/clawsjoy/data/memory/tenant_{tenant_id}.json")
        self.load()
    
    def load(self):
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                self.data = json.load(f)
        else:
            self.data = {
                "tasks": [],        # 任务历史
                "skills": {},       # Skill 统计
                "preferences": {},  # 用户偏好
                "knowledge": []     # 知识积累
            }
    
    def save(self):
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    # 任务记忆
    def remember_task(self, task_type, input_data, output, success=True):
        self.data["tasks"].append({
            "type": task_type,
            "input": input_data,
            "output": output[:300] if output else None,
            "success": success,
            "time": datetime.now().isoformat()
        })
        if len(self.data["tasks"]) > 100:
            self.data["tasks"] = self.data["tasks"][-100:]
        self.save()
    
    def recall_task(self, task_type):
        """回忆成功的任务经验"""
        for task in reversed(self.data["tasks"]):
            if task["type"] == task_type and task["success"]:
                return task["output"]
        return None
    
    # Skill 统计
    def record_skill(self, skill_name, success, duration):
        if skill_name not in self.data["skills"]:
            self.data["skills"][skill_name] = {"total": 0, "success": 0, "total_duration": 0}
        s = self.data["skills"][skill_name]
        s["total"] += 1
        if success:
            s["success"] += 1
        s["total_duration"] += duration
        s["avg_duration"] = s["total_duration"] / s["total"]
        s["success_rate"] = s["success"] / s["total"]
        self.save()
    
    def get_skill_score(self, skill_name):
        s = self.data["skills"].get(skill_name)
        if not s:
            return 50
        return s["success_rate"] * 100
    
    # 偏好
    def set_preference(self, key, value):
        self.data["preferences"][key] = value
        self.save()
    
    def get_preference(self, key, default=None):
        return self.data["preferences"].get(key, default)
    
    # 知识
    def add_knowledge(self, category, content):
        self.data["knowledge"].append({
            "category": category,
            "content": content,
            "time": datetime.now().isoformat()
        })
        if len(self.data["knowledge"]) > 200:
            self.data["knowledge"] = self.data["knowledge"][-200:]
        self.save()
    
    def search_knowledge(self, keyword):
        return [k for k in self.data["knowledge"] if keyword in k["content"]]
    
    def report(self):
        print("=" * 50)
        print("🧠 记忆系统报告")
        print("=" * 50)
        print(f"任务数: {len(self.data['tasks'])}")
        print(f"Skill数: {len(self.data['skills'])}")
        print(f"知识数: {len(self.data['knowledge'])}")
        for name, s in self.data["skills"].items():
            print(f"  {name}: {s['success_rate']*100:.0f}%")
        print("=" * 50)

def execute(params):
    memory = ClawsJoyMemory(params.get("tenant_id", "1"))
    action = params.get("action")
    
    if action == "remember":
        memory.remember_task(params["task_type"], params.get("input"), params.get("output"), params.get("success", True))
        return {"success": True}
    elif action == "recall":
        result = memory.recall_task(params["task_type"])
        return {"success": True, "memory": result}
    elif action == "skill":
        memory.record_skill(params["skill"], params["success"], params.get("duration", 0))
        return {"success": True, "score": memory.get_skill_score(params["skill"])}
    elif action == "preference":
        if "value" in params:
            memory.set_preference(params["key"], params["value"])
            return {"success": True}
        else:
            return {"success": True, "value": memory.get_preference(params["key"])}
    elif action == "knowledge":
        memory.add_knowledge(params["category"], params["content"])
        return {"success": True}
    elif action == "search":
        results = memory.search_knowledge(params["keyword"])
        return {"success": True, "results": results}
    elif action == "report":
        memory.report()
        return {"success": True}
    
    return {"error": f"未知 action: {action}"}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        import json
        params = json.loads(sys.argv[1])
        print(execute(params))
