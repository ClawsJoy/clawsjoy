import re

file_path = "agents/analysis_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 添加学习功能
learning_code = '''
    def learn(self, feedback: str) -> Dict:
        """从反馈中学习"""
        import json
        from pathlib import Path
        
        learning_file = Path("data/learning/feedback.json")
        learning_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {}
        if learning_file.exists():
            with open(learning_file, 'r') as f:
                data = json.load(f)
        
        data[len(data)] = {"feedback": feedback, "timestamp": __import__("time").time()}
        
        with open(learning_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"success": True, "message": "反馈已记录"}
'''

content = content.replace("class AnalysisAgent:", "class AnalysisAgent:\n" + learning_code)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 学习功能已集成到分析师")
