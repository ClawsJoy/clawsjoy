"""完整视频制作技能 - 图片轮播 + TTS配音 + 背景音乐 + 字幕"""

from typing import Dict
from skills.skill_interface import BaseSkill
import subprocess
import os
import requests
from datetime import datetime

class SlideshowMakerSkill(BaseSkill):
    name = "slideshow_maker"
    description = "制作完整视频（图片轮播 + TTS配音 + 背景音乐 + 字幕）"
    version = "2.0.0"
    category = "video"
    
    def execute(self, params: Dict) -> Dict:
        images = params.get("images", [])
        script = params.get("script", "")
        bgm_path = params.get("bgm", "assets/bgm/default.mp3")
        duration_per_image = params.get("duration_per_image", 4)
        
        if not images:
            return {"success": False, "error": "No images provided"}
        
        cwd = os.getcwd()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_dir = os.path.join(cwd, f"tmp/video_{timestamp}")
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(os.path.join(cwd, "output/videos"), exist_ok=True)
        
        # 1. 下载图片
        downloaded = []
        for i, img in enumerate(images[:10]):
            url = img.get('url') if isinstance(img, dict) else img
            try:
                resp = requests.get(url, timeout=10)
                img_path = os.path.join(temp_dir, f"img_{i:03d}.jpg")
                with open(img_path, 'wb') as f:
                    f.write(resp.content)
                downloaded.append(img_path)
            except Exception as e:
                print(f"⚠️ 下载失败: {e}")
        
        if not downloaded:
            return {"success": False, "error": "No images downloaded"}
        
        # 2. 生成配音（TTS）
        audio_file = os.path.join(temp_dir, "audio.mp3")
        if script:
            print("🎤 生成配音...")
            # 使用 edge-tts
            safe_script = script.replace('"', '\\"').replace('\n', ' ')
            cmd = f'edge-tts --text "{safe_script[:500]}" --voice zh-CN-XiaoxiaoNeural --write-media "{audio_file}"'
            try:
                subprocess.run(cmd, shell=True, timeout=60, capture_output=True)
                has_audio = os.path.exists(audio_file) and os.path.getsize(audio_file) > 0
            except:
                has_audio = False
        else:
            has_audio = False
        
        # 3. 创建视频（图片轮播）
        print("🎬 制作视频...")
        video_temp = os.path.join(temp_dir, "video_no_audio.mp4")
        concat_file = os.path.join(temp_dir, "concat.txt")
        
        with open(concat_file, 'w') as f:
            for img_path in downloaded:
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration_per_image}\n")
        
        # 计算视频时长
        video_duration = duration_per_image * len(downloaded)
        
        cmd_video = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -pix_fmt yuv420p -t {video_duration} "{video_temp}"'
        subprocess.run(cmd_video, shell=True, capture_output=True)
        
        # 4. 添加配音+背景音乐
        output_file = os.path.join(cwd, f"output/videos/video_{timestamp}.mp4")
        
        if has_audio:
            # 合并视频 + 配音 + 背景音乐
            print("🎵 合成音频...")
            mixed_audio = os.path.join(temp_dir, "mixed_audio.mp3")
            if os.path.exists(bgm_path):
                mix_cmd = f'ffmpeg -y -i "{audio_file}" -i "{bgm_path}" -filter_complex "[0:a]volume=1[a1];[1:a]volume=0.15[a2];[a1][a2]amix=inputs=2" -c:a libmp3lame "{mixed_audio}"'
                subprocess.run(mix_cmd, shell=True, capture_output=True)
                audio_source = mixed_audio
            else:
                audio_source = audio_file
            
            # 添加字幕
            subtitle_filter = ""
            if script:
                # 创建字幕文件
                srt_file = os.path.join(temp_dir, "subtitle.srt")
                with open(srt_file, 'w') as f:
                    f.write("1\n00:00:00,000 --> 00:00:05,000\n")
                    f.write(script[:100] + "\n\n")
                
                subtitle_filter = f'-vf "subtitles={srt_file}"'
            
            final_cmd = f'ffmpeg -y -i "{video_temp}" -i "{audio_source}" {subtitle_filter} -c:v libx264 -c:a aac -shortest "{output_file}"'
        else:
            # 无配音，只加背景音乐
            if os.path.exists(bgm_path):
                final_cmd = f'ffmpeg -y -i "{video_temp}" -i "{bgm_path}" -c:v libx264 -c:a aac -shortest "{output_file}"'
            else:
                final_cmd = f'ffmpeg -y -i "{video_temp}" -c:v libx264 "{output_file}"'
        
        subprocess.run(final_cmd, shell=True, capture_output=True)
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return {
                "success": True,
                "video_file": output_file,
                "image_count": len(downloaded),
                "duration": video_duration,
                "has_audio": has_audio,
                "script_length": len(script)
            }
        
        return {"success": False, "error": "Video creation failed"}

skill = SlideshowMakerSkill()
