"""知识自增长器 - 从交互中学习新知识"""

import json
from pathlib import Path
from datetime import datetime
from core.lib.smart_adapter import smart_adapter
from core.lib.knowledge_registry import knowledge_registry


class KnowledgeGrower:
    """
    知识自增长器
    
    从用户交互中提取新知识，自动存入知识库
    """
    
    def __init__(self):
        self.learned_file = Path("data/learned_knowledge.json")
        self._load_learned()
    
    def _load_learned(self):
        if self.learned_file.exists():
            with open(self.learned_file, 'r') as f:
                self.learned = json.load(f)
        else:
            self.learned = {"facts": [], "patterns": [], "insights": []}
    
    def _save_learned(self):
        with open(self.learned_file, 'w') as f:
            json.dump(self.learned, f, indent=2)
    
    def learn_from_conversation(self, user_input: str, response: str):
        """从对话中学习"""
        # 提取事实
        prompt = f"""从以下对话中提取新知识或事实。

用户: {user_input}
助手: {response}

如果有新知识，输出JSON:
{{"fact": "提取的知识", "category": "分类", "confidence": 0-100}}

如果没有新知识，输出: {{"has_knowledge": false}}"""

        result = smart_adapter.generate(prompt, auto_select=True)
        
        import re
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            import json
            data = json.loads(match.group())
            if data.get("fact"):
                # 存入知识库
                knowledge_registry.add_knowledge(
                    title=f"从对话学到的知识",
                    content=data["fact"],
                    category=data.get("category", "learned"),
                    source="conversation"
                )
                self.learned["facts"].append({
                    "fact": data["fact"],
                    "source": user_input[:50],
                    "learned_at": datetime.now().isoformat()
                })
                self._save_learned()
                print(f"📚 学到新知识: {data['fact'][:50]}...")
    
    def learn_from_success(self, goal: str, plan: list, result: str):
        """从成功执行中学习"""
        insight = {
            "goal": goal[:100],
            "plan": plan,
            "result": result[:200],
            "timestamp": datetime.now().isoformat()
        }
        self.learned["insights"].append(insight)
        self.learned["insights"] = self.learned["insights"][-50:]
        self._save_learned()
        
        print(f"💡 获得新洞察: {goal[:50]}...")


knowledge_grower = KnowledgeGrower()
