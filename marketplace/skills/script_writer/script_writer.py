"""脚本生成技能"""

from typing import Dict
from skills.skill_interface import BaseSkill
import requests
import os
from datetime import datetime

class ScriptWriterSkill(BaseSkill):
    name = "script_writer"
    description = "根据主题生成视频脚本"
    version = "1.0.0"
    category = "content"
    
    def execute(self, params: Dict) -> Dict:
        topic = params.get("topic", "")
        style = params.get("style", "科普")
        
        # 如果有规划的主题，使用它
        planned_topics = params.get("planned_topics", [])
        context = ""
        if planned_topics:
            context = "规划的主题:\n" + "\n".join([f"- {t}" for t in planned_topics])
        
        prompt = f"""主题: {topic}
{context}

请生成一个{style}风格的视频脚本，长度约2-3分钟。"""
        
        try:
            resp = requests.post("http://localhost:11434/api/generate",
                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                timeout=90)
            script = resp.json().get('response', '')
            
            # 保存脚本文件
            script_dir = "data/scripts"
            os.makedirs(script_dir, exist_ok=True)
            script_file = f"{script_dir}/script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)
            
            return {
                "success": True,
                "script": script,           # 直接返回脚本内容
                "script_file": script_file, # 同时返回文件路径
                "topic": topic,
                "style": style,
                "length": len(script)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = ScriptWriterSkill()
