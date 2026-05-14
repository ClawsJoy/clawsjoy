"""Whisper 转写原子技能"""
import whisper
import os

class WhisperTranscribeSkill:
    name = "whisper_transcribe"
    description = "本地语音转文字，使用 OpenAI Whisper"
    version = "1.0.0"
    category = "audio"

    def __init__(self):
        self.model = None
        self.model_name = "tiny"

    def _load_model(self):
        if self.model is None:
            self.model = whisper.load_model(self.model_name)
        return self.model

    def execute(self, params):
        audio_path = params.get("audio_path")
        language = params.get("language", "zh")
        
        if not audio_path:
            return {"success": False, "error": "缺少 audio_path 参数"}
        
        if not os.path.exists(audio_path):
            return {"success": False, "error": f"音频文件不存在: {audio_path}"}
        
        try:
            model = self._load_model()
            result = model.transcribe(audio_path, language=language)
            text = result.get("text", "").strip()
            return {
                "success": True,
                "text": text,
                "language": language,
                "audio_path": audio_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# 创建全局实例（这是关键，skill_registry 需要这个）
skill = WhisperTranscribeSkill()
