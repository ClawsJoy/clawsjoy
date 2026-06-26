"""TTS配音 - 分镜对白自动配音"""
import edge_tts, asyncio
from pathlib import Path

class TTSDubbing:
    def __init__(self, output_dir="data/voice_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.voices = {
            "林浩": "zh-CN-YunxiNeural",
            "无名": "zh-CN-XiaoxiaoNeural",
            "艾丽卡": "zh-CN-XiaoyiNeural",
        }
    
    async def dub_line(self, role, text, filename=None):
        voice = self.voices.get(role, "zh-CN-XiaoxiaoNeural")
        if not filename:
            safe = text[:10].replace("?", "").replace("。", "")
            filename = f"{role}_{safe}.mp3"
        path = self.output_dir / filename
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(path))
        return str(path)
    
    def dub_sync(self, role, text, filename=None):
        return asyncio.run(self.dub_line(role, text, filename))
    
    def dub_storyboard(self, storyboard_lines):
        results = []
        for line in storyboard_lines:
            role, text = line.get("role"), line.get("text")
            if role and text:
                path = self.dub_sync(role, text)
                results.append({"role": role, "text": text, "audio": path})
        return results

dubbing = TTSDubbing()
