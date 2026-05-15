"""文案生成技能 - 通过 Ollama 生成脚本"""

from typing import Dict
from skills.skill_interface import BaseSkill
import subprocess
import re
import os

class ScriptGeneratorSkill(BaseSkill):
    name = "script_generator"
    description = "生成视频脚本（纯文本，无格式）"
    version = "1.0.0"
    category = "content"
    
    def execute(self, params: Dict) -> Dict:
        topic = params.get("topic", params.get("keyword", "香港"))
        length = params.get("length", 300)
        style = params.get("style", "宣传")
        
        prompt = f"""写一篇{length}字左右的{style}文案，介绍{topic}。
要求：纯文本，不要任何 markdown 标记（不要 #、*、**、- 等）。
直接输出文案内容。"""
        
        try:
            # 方法1: 使用 ollama 命令行
            result = subprocess.run(
                ['ollama', 'run', 'qwen2.5:7b', prompt],
                capture_output=True, text=True, timeout=60
            )
            script = result.stdout.strip()
        except:
            # 方法2: 使用 HTTP API
            import requests
            resp = requests.post("http://localhost:11434/api/generate",
                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                timeout=60)
            script = resp.json().get('response', '')
        
        # 清理格式
        script = re.sub(r'\*\*+', '', script)
        script = re.sub(r'#{3,}', '', script)
        script = re.sub(r'^[-*] ', '', script, flags=re.MULTILINE)
        
        # 保存到文件
        from datetime import datetime
        script_dir = "data/scripts"
        os.makedirs(script_dir, exist_ok=True)
        script_file = f"{script_dir}/script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return {
            "success": True,
            "script": script,
            "script_file": script_file,
            "length": len(script),
            "topic": topic
        }

skill = ScriptGeneratorSkill()
