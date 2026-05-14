import os
import subprocess
import re
import requests
from skills.spider import skill as spider
from skills.character_designer import skill as char
from skills.tts import skill as tts
from skills.add_subtitles import skill as subtitle

class ManjuMakerSkill:
    name = "manju_maker"
    description = "一键生成漫剧视频"
    version = "2.0.0"
    category = "video"

    SCENE_MAP = {
        "街道": "hongkong_street",
        "办公室": "hongkong_office",
        "家": "hongkong_home",
        "维港": "hongkong_victoria_harbour",
    }

    def execute(self, params):
        topic = params.get("topic", "香港故事")
        base_dir = "/mnt/d/clawsjoy"

        print(f"🎬 制作漫剧: {topic}")

        # 1. 生成脚本
        print("📝 生成脚本...")
        script_prompt = f"""为「{topic}」生成一个短视频脚本。输出JSON: {{"narration": "旁白内容"}}"""
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                             json={"model": "qwen2.5:7b", "prompt": script_prompt,
                                   "stream": False, "temperature": 0.7})
        raw = resp.json()["response"]
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                import json
                data = json.loads(match.group())
                narration = data.get("narration", topic)
            except:
                narration = topic
        else:
            narration = topic

        print(f"   脚本长度: {len(narration)}")

        # 2. 角色
        print("👤 生成角色...")
        char_result = char.create_character({'name': '主角'})
        character_img = char_result.get('image')

        # 3. 背景图
        print("🖼️ 下载背景图...")
        scenes = ["hongkong_victoria_harbour", "hongkong_office", "hongkong_home"]
        bg_paths = []
        for scene in scenes:
            result = spider.execute({'mode': 'images', 'keyword': scene, 'count': 1, 'save_dir': 'output/bg'})
            if result.get('images'):
                bg_paths.append(result['images'][0])
                print(f"  ✅ {scene}")

        if not bg_paths:
            bg_paths = [f"{base_dir}/output/bg/city.jpg", f"{base_dir}/output/bg/office.jpg", f"{base_dir}/output/bg/home.jpg"]

        # 4. TTS
        print("🔊 生成配音...")
        audio_path = f"{base_dir}/output/tts_manju.mp3"
        tts.execute({'text': narration[:800], 'output_path': audio_path})

        # 5. 获取时长
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                                capture_output=True, text=True)
        duration = float(result.stdout.strip()) if result.stdout.strip() else 60
        per_scene = duration / len(bg_paths)

        # 6. 合成
        concat_file = "/tmp/manju_concat.txt"
        with open(concat_file, "w") as f:
            for bg in bg_paths:
                abs_bg = bg if bg.startswith('/') else f"{base_dir}/{bg}"
                f.write(f"file '{abs_bg}'\n")
                f.write(f"duration {per_scene}\n")

        no_char_video = f"{base_dir}/output/no_char_video.mp4"
        cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file,
               '-i', audio_path,
               '-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-pix_fmt', 'yuv420p',
               no_char_video]
        subprocess.run(cmd, capture_output=True)

        # 7. 添加头像
        final_video = no_char_video
        if character_img and os.path.exists(character_img):
            with_char_video = f"{base_dir}/output/with_char_video.mp4"
            overlay_cmd = ['ffmpeg', '-y', '-i', no_char_video,
                           '-i', character_img,
                           '-filter_complex', '[1:v]scale=100:-1[char];[0:v][char]overlay=W-w-20:H-h-20',
                           '-c:a', 'copy', with_char_video]
            subprocess.run(overlay_cmd, capture_output=True)
            if os.path.exists(with_char_video):
                final_video = with_char_video

        # 8. 字幕
        safe_topic = topic.replace(' ', '_').replace('/', '_')
        output_path = f"{base_dir}/output/manju_{safe_topic}.mp4"
        subtitle.execute({'video_path': final_video, 'script': narration, 'output_path': output_path})

        # 清理
        for f in [no_char_video, f"{base_dir}/output/with_char_video.mp4"]:
            if os.path.exists(f) and f != output_path:
                os.remove(f)

        print(f"✅ 漫剧视频: {output_path} ({duration:.1f}秒)")
        return {"success": True, "video": output_path, "duration": duration, "script_length": len(narration)}

skill = ManjuMakerSkill()
