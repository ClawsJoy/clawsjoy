"""tts-dubbing 技能实现"""
import edge_tts, asyncio, os
from pathlib import Path

class tts_dubbing:
    name = "tts-dubbing"
    description = "漫剧分镜对白自动配音"
    version = "1.0.0"
    
    VOICES = {
        "林浩": "zh-CN-YunxiNeural",
        "无名": "zh-CN-XiaoxiaoNeural",
        "艾丽卡": "zh-CN-XiaoyiNeural",
    }
    
    def __init__(self):
        self.output_dir = Path("data/voice_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, params):
        lines = params.get("lines", [])
        if not lines:
            return {"success": False, "error": "请提供对白列表"}
        
        results = []
        for line in lines:
            role = line.get("role", "")
            text = line.get("text", "")
            if not role or not text:
                continue
            voice = self.VOICES.get(role, "zh-CN-XiaoxiaoNeural")
            safe = text[:10].replace("?", "").replace("。", "").replace(" ", "_")
            filename = f"{role}_{safe}.mp3"
            path = str(self.output_dir / filename)
            
            async def gen():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(path)
            asyncio.run(gen())
            
            results.append({"role": role, "text": text, "audio": path})
        
        return {"success": True, "files": results}
