import requests
import re

class HotDualScriptSkill:
    name = "hot_dual_script"
    description = "生成旁白脚本"
    version = "1.0.0"
    category = "script"

    def execute(self, params):
        topic = params.get("topic", "")
        
        prompt = f"为{topic}生成60秒短视频脚本，至少150字，直接输出脚本内容不要JSON。"
        
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                             json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False})
        narration = resp.json()["response"].strip()
        
        if len(narration) < 100:
            narration = f"今天聊聊{topic}。" + narration
        
        return {"narration": narration, "description": topic}

skill = HotDualScriptSkill()
