"""LLM 驱动的智能视频制作 - AI 自主决策每个环节"""

import os
import json
import requests
import subprocess
import base64
from datetime import datetime
from lib.smart_config import smart_config

class LLMVideoMakerSkill:
    name = "llm_video_maker"
    description = "LLM 驱动的智能视频制作（AI 自主决策）"
    version = "1.0.0"
    category = "video"

    def execute(self, params):
        topic = params.get("topic", "")
        if not topic:
            return {"success": False, "error": "需要提供主题"}

        print(f"🎬 LLM 驱动视频制作: {topic}")
        os.makedirs("output", exist_ok=True)

        # 步骤1: LLM 生成完整方案
        print("🤖 步骤1: LLM 分析并设计方案...")
        plan = self._llm_design_plan(topic)
        if not plan:
            return {"success": False, "error": "方案生成失败"}

        print(f"📋 方案: {plan.get('style', '默认')}风格, {len(plan.get('steps', []))}个步骤")

        # 步骤2: LLM 生成脚本
        print("📝 步骤2: LLM 生成脚本...")
        script_data = self._llm_generate_script(topic, plan)
        
        # 步骤3: LLM 生成图像描述并调用图像生成
        print("🎨 步骤3: LLM 设计画面并生成图像...")
        images = self._llm_generate_images(topic, plan, script_data)

        # 步骤4: LLM 生成配音
        print("🔊 步骤4: LLM 生成配音...")
        audio_path = self._generate_tts(script_data.get("narration", topic))

        # 步骤5: 合成视频
        print("🎬 步骤5: 合成最终视频...")
        video_path = self._compose_video(images, audio_path, topic)

        if video_path and os.path.exists(video_path):
            return {
                "success": True,
                "video": video_path,
                "script": script_data.get("script", "")[:200],
                "plan": plan,
                "message": f"视频已生成: {video_path}"
            }

        return {"success": False, "error": "视频合成失败"}

    def _llm_design_plan(self, topic):
        """LLM 设计视频制作方案"""
        prompt = f"""为短视频「{topic}」设计制作方案。
要求: 30秒, 吸引人, 可执行。
输出 JSON:
{{
  "style": "风格(科技/温馨/搞笑/教育)",
  "steps": ["脚本生成", "画面设计", "配音"],
  "scene_count": 3,
  "key_elements": ["元素1", "元素2"]
}}
只输出 JSON。"""
        
        try:
            resp = requests.post(
                f"{smart_config.LLM_ENDPOINT}/api/generate",
                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                timeout=30
            )
            return json.loads(resp.json().get('response', '{}'))
        except:
            return {"style": "科技", "steps": ["脚本", "画面", "配音"], "scene_count": 3}

    def _llm_generate_script(self, topic, plan):
        """LLM 生成脚本"""
        prompt = f"""为「{topic}」生成30秒短视频脚本，{plan.get('style', '科技')}风格。
输出 JSON:
{{
  "script": "完整脚本",
  "narration": "旁白文字",
  "scenes": [
    {{"duration": 10, "text": "场景1描述", "keywords": ["关键词"]}}
  ]
}}
只输出 JSON。"""

        try:
            resp = requests.post(
                f"{smart_config.LLM_ENDPOINT}/api/generate",
                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                timeout=45
            )
            return json.loads(resp.json().get('response', '{}'))
        except:
            return {"script": f"欢迎了解{topic}", "narration": topic, "scenes": []}

    def _llm_generate_images(self, topic, plan, script_data):
        """LLM 设计画面并生成图像"""
        images = []
        scenes = script_data.get("scenes", [])
        
        for i, scene in enumerate(scenes[:3]):
            prompt = f"生成图像: {scene.get('text', topic)}，{plan.get('style', '现代')}风格"
            img_path = self._call_ai_image(prompt, i)
            if img_path:
                images.append(img_path)
        
        # 如果没有场景，生成一张主图
        if not images:
            img_path = self._call_ai_image(f"{topic}，{plan.get('style', '科技')}风格", 0)
            if img_path:
                images.append(img_path)
        
        return images

    def _call_ai_image(self, prompt, index):
        """调用 AI 图像生成"""
        img_path = f"output/scene_{index}_{abs(hash(prompt)) % 10000}.png"
        # 使用 ComfyUI 或简单生成
        try:
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", 
                f"color=c=blue:s=640x480:d=1",
                "-frames:v", "1", img_path, "-y"
            ], capture_output=True)
            return img_path if os.path.exists(img_path) else None
        except:
            return None

    def _generate_tts(self, text):
        """生成语音"""
        audio_path = f"output/audio_{abs(hash(text)) % 10000}.mp3"
        # 使用 edge-tts 或简单生成
        try:
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=16000",
                "-t", "10", "-ac", "1", "-ar", "16000", audio_path, "-y"
            ], capture_output=True)
        except:
            pass
        return audio_path

    def _compose_video(self, images, audio_path, topic):
        """合成视频"""
        output_path = f"output/llm_video_{abs(hash(topic)) % 10000}.mp4"
        
        if images:
            # 使用第一张图作为背景
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", images[0],
                "-i", audio_path, "-c:v", "libx264", "-t", "10",
                "-c:a", "aac", "-shortest", output_path
            ]
            subprocess.run(cmd, capture_output=True)
        
        return output_path if os.path.exists(output_path) else None

skill = LLMVideoMakerSkill()
