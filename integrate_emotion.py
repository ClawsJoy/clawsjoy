import re

# 修改分析师，集成情感分析
file_path = "agents/analysis_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 添加情感分析功能
if "def analyze_emotion" not in content:
    emotion_code = '''
    def analyze_emotion(self, text: str) -> Dict:
        """情感分析"""
        import requests
        try:
            resp = requests.post(
                "http://localhost:5012/chat",
                json={"message": f"分析这段文字的情感(积极/消极/中性): {text}"},
                timeout=10
            )
            if resp.status_code == 200:
                return {"emotion": resp.json().get("response", "中性")}
        except Exception as e:
            pass
        return {"emotion": "中性"}
    
    def process(self, user_input: str, context: Dict = None) -> Dict:
        """分析师入口 - 集成情感分析"""
        emotion = self.analyze_emotion(user_input)
        return {
            "success": True,
            "emotion": emotion.get("emotion"),
            "intent": self._detect_intent(user_input),
            "agent": "analysis_agent"
        }
'''

# 在类中添加
content = content.replace("class AnalysisAgent:", "class AnalysisAgent:\n" + emotion_code)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 情感分析已集成到分析师")
