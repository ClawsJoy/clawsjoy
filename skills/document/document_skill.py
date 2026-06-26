"""文档处理"""
import requests

class document_skill:
    name = "document"
    description = "文档格式转换和处理"
    version = "1.0.0"
    
    def execute(self, params):
        text = params.get("text", "")
        action = params.get("action", "summarize")
        prompt = f"{action}: {text[:1000]}"
        r = requests.post('http://127.0.0.1:11434/api/generate', json={
            'model': 'qwen2.5:7b', 'prompt': prompt, 'stream': False
        }, timeout=30)
        return {"success": True, "result": r.json().get('response', '')}
