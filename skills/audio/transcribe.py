"""音频转录技能 - 使用 Vosk"""

import json
import wave
import vosk
from pathlib import Path

def execute(params: dict) -> dict:
    """转录音频文件"""
    audio_path = params.get('audio_path', '')
    
    if not audio_path:
        return {"success": False, "error": "audio_path required"}
    
    # 初始化 Vosk 模型
    model = vosk.Model("models/vosk-model-small-cn-0.22")
    rec = vosk.KaldiRecognizer(model, 16000)
    
    # 读取音频文件
    wf = wave.open(audio_path, "rb")
    text = []
    
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text.append(result.get('text', ''))
    
    final = json.loads(rec.FinalResult())
    text.append(final.get('text', ''))
    
    return {
        "success": True,
        "transcript": ' '.join(text),
        "audio": audio_path
    }
