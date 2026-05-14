"""TTS 文字转语音原子技能"""
import subprocess
import os
from pathlib import Path

class TTSSkill:
    name = "tts"
    description = "文字转语音（使用 edge-tts）"
    version = "1.0.0"
    category = "audio"

    def execute(self, params):
        text = params.get("text", "")
        voice = params.get("voice", "zh-CN-XiaoxiaoNeural")
        output_path = params.get("output_path", "output/tts_audio.mp3")

        if not text:
            return {"success": False, "error": "缺少 text 参数"}

        # ✅ 确保 output_path 不是空字符串
        if not output_path:
            output_path = "output/tts_audio.mp3"

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 使用 edge-tts 生成语音
        cmd = f'edge-tts --text "{text}" --voice {voice} --write-media {output_path}'

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return {
                    "success": True,
                    "audio_path": output_path,
                    "voice": voice,
                    "text_length": len(text)
                }
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = TTSSkill()
