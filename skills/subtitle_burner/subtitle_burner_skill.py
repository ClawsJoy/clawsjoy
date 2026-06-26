"""字幕烧录技能 - TTS配音+字幕+嵌入视频"""
import edge_tts, asyncio, subprocess, json, os, re, tempfile
from pathlib import Path

class subtitle_burner:
    name = "subtitle-burner"
    description = "TTS配音+字幕生成+嵌入视频"
    version = "1.0.0"
    
    VOICES = {
        "林浩": "zh-CN-YunxiNeural",
        "无名": "zh-CN-XiaoxiaoNeural",
    }
    
    def execute(self, params):
        video_path = params.get("video", "")
        lines = params.get("lines", [])
        output = params.get("output", "")
        
        if not video_path or not lines:
            return {"success": False, "error": "请提供video和lines"}
        
        if not output:
            output = video_path.replace(".mp4", "_配音版.mp4")
        
        tmp_dir = tempfile.mkdtemp()
        audio_files = []
        srt_files = []
        
        for i, line in enumerate(lines):
            role = line.get("role", "旁白")
            text = line.get("text", "")
            start_time = line.get("start", i * 4)  # 秒
            
            voice = self.VOICES.get(role, "zh-CN-XiaoxiaoNeural")
            audio_path = f"{tmp_dir}/line_{i:02d}.mp3"
            srt_path = f"{tmp_dir}/line_{i:02d}.srt"
            
            # TTS
            async def gen():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(audio_path)
            asyncio.run(gen())
            
            # 字幕
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', audio_path
            ], capture_output=True, text=True)
            duration = float(json.loads(result.stdout)['format']['duration'])
            
            with open(srt_path, 'w') as f:
                def fmt(t):
                    t += start_time
                    return f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(t%1*1000):03d}"
                f.write(f"1\n{fmt(0)} --> {fmt(duration)}\n{text}\n\n")
            
            audio_files.append(audio_path)
            srt_files.append(srt_path)
        
        # 合并字幕
        all_srt = f"{tmp_dir}/all.srt"
        with open(all_srt, 'w') as out:
            idx = 1
            for srt in srt_files:
                with open(srt) as f:
                    content = f.read()
                content = re.sub(r'^\d+', str(idx), content, flags=re.MULTILINE)
                out.write(content)
                idx += 1
        
        # 合并音频
        audio_list = f"{tmp_dir}/audio_list.txt"
        with open(audio_list, 'w') as f:
            for a in audio_files:
                f.write(f"file '{a}'\n")
        all_audio = f"{tmp_dir}/all_audio.mp3"
        subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', audio_list,
                      '-c', 'copy', all_audio], capture_output=True)
        
        # 嵌入视频
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path, '-i', all_audio,
            '-vf', f"subtitles={all_srt}:force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2'",
            '-c:v', 'libx264', '-c:a', 'aac', '-shortest',
            output
        ], capture_output=True)
        
        return {"success": True, "output": output, "subtitles": len(lines), "lines": lines}
