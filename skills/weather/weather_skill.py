"""天气查询"""
import requests

class weather_skill:
    name = "weather"
    description = "天气查询"
    version = "1.0.0"
    
    def execute(self, params):
        city = params.get("city", "北京")
        prompt = f"查询{city}今天的天气，给出简短回答。"
        r = requests.post('http://127.0.0.1:11434/api/generate', json={
            'model': 'qwen2.5:7b', 'prompt': prompt, 'stream': False
        }, timeout=30)
        return {"success": True, "weather": r.json().get('response', '')}
