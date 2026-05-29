"""通用音频处理技能 - 语音识别、格式转换、音频分析"""

import json
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any

description = "audio_processor 音频处理 语音识别 音频转文字 格式转换 音频分析 裁剪 合并 降噪"


class AudioProcessor:
    """音频处理器"""
    
    def __init__(self):
        self.supported_actions = ["transcribe", "convert", "analyze", "trim", "merge"]
        self.supported_formats = ["mp3", "wav", "ogg", "flac", "m4a"]
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        action = params.get('action', '')
        source = params.get('source', '')
        source_data = params.get('source_data', '')
        
        if not action:
            return {"error": "缺少 action 参数", "supported_actions": self.supported_actions}
        
        if action == "analyze":
            return self._analyze(source_data)
        elif action == "transcribe":
            return self._transcribe(source_data, params.get('options', {}))
        elif action == "convert":
            return self._convert(source_data, params.get('target_format', ''))
        else:
            return {"error": f"不支持的操作: {action}", "supported": self.supported_actions}
    
    def _analyze(self, audio_path: str) -> Dict:
        """分析音频"""
        if not os.path.exists(audio_path):
            return {"error": f"文件不存在: {audio_path}"}
        
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', audio_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"error": "无法读取音频信息"}
            
            data = json.loads(result.stdout)
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    return {
                        "success": True,
                        "duration": float(stream.get('duration', 0)),
                        "sample_rate": int(stream.get('sample_rate', 0)),
                        "channels": int(stream.get('channels', 0)),
                        "codec": stream.get('codec_name', 'unknown')
                    }
            return {"error": "未找到音频流"}
        except Exception as e:
            return {"error": f"分析失败: {str(e)}"}
    
    def _transcribe(self, audio_path: str, options: Dict) -> Dict:
        """语音识别"""
        return {"success": False, "error": "语音识别功能需要安装 Vosk 模型", "note": "请先下载模型: cd models/vosk && wget https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip && unzip vosk-model-small-cn-0.22.zip"}
    
    def _convert(self, audio_path: str, target_format: str) -> Dict:
        """格式转换"""
        return {"success": False, "error": "格式转换需要安装 ffmpeg"}


# 导出技能实例（关键！）
skill = AudioProcessor()
