from lib.smart_config import smart_config
"""音频质量检查器"""
from pathlib import Path
import subprocess

class AudioQualityCheckSkill:
    name = "audio_quality_check"
    description = "检查音频质量"
    version = "1.0.0"
    category = "audio"
    
    def execute(self, params):
        audio_path = params.get("audio_path", "")
        
        if not audio_path or not Path(audio_path).exists():
            return {"success": False, "error": "音频不存在"}
        
        size_kb = Path(audio_path).stat().st_size / 1024
        
        # 获取时长
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                capture_output=True, text=True
            )
            duration = float(result.stdout.strip()) if result.stdout else 0
        except:
            duration = 0
        
        issues = []
        if duration < 5:
            issues.append(f"音频太短: {duration:.1f}秒")
        if size_kb < 10:
            issues.append(f"文件太小: {size_kb:.1f}KB")
        
        return {
            "success": len(issues) == 0,
            "duration": round(duration, 1),
            "size_kb": round(size_kb, 1),
            "issues": issues,
            "quality_score": max(0, 100 - len(issues) * 25)
        }

skill = AudioQualityCheckSkill()
