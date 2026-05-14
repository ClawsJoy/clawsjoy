"""字幕生成 - 正确版本"""
import subprocess
import re

class AddSubtitlesSkill:
    name = "add_subtitles"
    description = "为视频添加字幕"
    version = "2.0.0"
    category = "video"

    def execute(self, params):
        video_path = params.get("video_path", "")
        script = params.get("script", "")
        output_path = params.get("output_path", "output/subtitled.mp4")
        
        if not video_path or not script:
            return {"error": "缺少视频路径或脚本"}
        
        # 获取视频时长
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
                                capture_output=True, text=True)
        total_duration = float(result.stdout.strip()) if result.stdout.strip() else 60
        
        # 按句子分割
        sentences = re.split(r'[。！？!?]', script)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            sentences = [script[:100]]
        
        # 每句时长
        duration_per = total_duration / len(sentences)
        
        # 生成 SRT
        srt_path = "/tmp/subtitle.srt"
        lines = []
        for i, sent in enumerate(sentences):
            start = i * duration_per
            end = (i + 1) * duration_per
            lines.append(f"{i+1}")
            lines.append(f"{int(start//60):02d}:{int(start%60):02d}:{int((start%1)*1000):03d} --> {int(end//60):02d}:{int(end%60):02d}:{int((end%1)*1000):03d}")
            lines.append(sent)
            lines.append("")
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        # 烧录
        cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', f"subtitles={srt_path}",
               '-c:a', 'copy', output_path]
        subprocess.run(cmd, capture_output=True)
        
        return {"success": True, "output": output_path, "subtitle_count": len(sentences)}

skill = AddSubtitlesSkill()
