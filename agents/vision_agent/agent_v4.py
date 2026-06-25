#!/usr/bin/env python3
"""VisionAgent v5.0 - 视觉创作与图像分析"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class VisionAgentV4(BusinessAgent):
    name = "vision_agent_v4"
    description = "视觉创作与图像分析"
    version = "5.0.0"

    STYLES = ["写实", "动漫", "水彩", "油画", "素描", "像素", "3D渲染", "赛博朋克", "水墨", "浮世绘"]
    RATIOS = {"方形": "1:1", "横版": "16:9", "竖版": "9:16", "漫画": "3:4"}

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.output_dir = Path(f"data/vision/{user_id}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"👁 VisionAgent v{self.version}")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.9)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()

        if any(kw in t for kw in ["生成", "画", "创建", "绘制"]):
            return self._generate(user_input)
        elif any(kw in t for kw in ["分析", "识别", "描述图"]):
            return self._analyze(user_input)
        elif any(kw in t for kw in ["角色立绘", "人物图"]):
            return self._character_sheet(user_input)
        elif any(kw in t for kw in ["场景图", "背景"]):
            return self._scene_image(user_input)
        elif any(kw in t for kw in ["分镜画面", "漫剧画面"]):
            return self._storyboard_frame(user_input)
        elif any(kw in t for kw in ["风格", "画风"]):
            return self._list_styles()
        else:
            return self._help()

    def _generate(self, user_input: str) -> Dict:
        """通用图像生成"""
        prompt = self._clean_prompt(user_input)
        style = self._detect_style(user_input)
        ratio = self._detect_ratio(user_input)

        # 用LLM优化提示词
        enhanced = self._call_llm(
            f"作为AI绘画专家，将以下描述优化为Stable Diffusion英文提示词，包含画风、光照、构图、细节：\n\n{prompt}\n\n风格：{style}\n比例：{ratio}\n\n只输出英文提示词：",
            task_type="prompt_enhance"
        )

        return self._resp(
            f"## 🎨 图像生成\n\n"
            f"**提示词**: {prompt}\n"
            f"**风格**: {style}  |  **比例**: {self.RATIOS.get(ratio, ratio)}\n"
            f"**增强提示词**: `{enhanced or prompt}`\n\n"
            f"💡 可接入 Stable Diffusion / Midjourney / DALL-E 生成实际图像\n"
            f"📁 输出目录: {self.output_dir}"
        )

    def _character_sheet(self, user_input: str) -> Dict:
        """角色立绘生成"""
        prompt = self._clean_prompt(user_input)

        enhanced = self._call_llm(
            f"生成角色立绘提示词，包含：全身像、服装细节、发型、表情、三视图(front/side/back)、白色背景、高质量：\n\n{prompt}\n\n只输出英文提示词：",
            task_type="character_sheet"
        )

        return self._resp(
            f"## 👤 角色立绘\n\n"
            f"**角色**: {prompt}\n"
            f"**提示词**: `{enhanced or prompt}`\n\n"
            f"💡 建议搭配 ControlNet OpenPose 控制姿态"
        )

    def _scene_image(self, user_input: str) -> Dict:
        """场景图生成"""
        prompt = self._clean_prompt(user_input)

        enhanced = self._call_llm(
            f"生成场景概念图提示词，包含：环境、氛围、光照、景深、广角、高质量：\n\n{prompt}\n\n只输出英文提示词：",
            task_type="scene_image"
        )

        return self._resp(
            f"## 🏞 场景图\n\n"
            f"**场景**: {prompt}\n"
            f"**提示词**: `{enhanced or prompt}`\n\n"
            f"💡 建议使用 16:9 横版比例"
        )

    def _storyboard_frame(self, user_input: str) -> Dict:
        """漫剧分镜画面"""
        prompt = self._clean_prompt(user_input)

        enhanced = self._call_llm(
            f"生成漫剧分镜画面提示词，包含：角色动作、表情、场景、镜头角度、漫画风格、清晰线条：\n\n{prompt}\n\n只输出英文提示词：",
            task_type="storyboard_frame"
        )

        return self._resp(
            f"## 🎬 分镜画面\n\n"
            f"**画面**: {prompt}\n"
            f"**提示词**: `{enhanced or prompt}`\n\n"
            f"💡 建议使用 3:4 比例，配合分镜脚本使用"
        )

    def _analyze(self, user_input: str) -> Dict:
        """图像分析 - 使用 llava 模型"""
        path = self._extract_path(user_input)
        if not path:
            return self._resp("请提供图像路径。例如：分析 data/vision/demo/characters/林浩/01_素体_正面.png")
        
        img_path = Path(path)
        if not img_path.exists():
            return self._resp(f"图像不存在: {path}")
        
        # 提取问题（"分析 xxx 有什么问题" → question）
        question = user_input.replace(path, "").strip()
        if not question or len(question) < 3:
            question = "描述这张图片的内容、画风、质量，是否有手指/面部畸形？"
        
        try:
            import base64, requests
            with open(img_path, 'rb') as f:
                img_b64 = base64.b64encode(f.read()).decode()
            
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llava:latest",
                    "prompt": question,
                    "images": [img_b64],
                    "stream": False
                },
                timeout=60
            )
            if resp.status_code == 200:
                description = resp.json().get('response', '无描述')
                return self._resp(
                    f"## 🖼 图像分析\n\n"
                    f"**文件**: {path}\n"
                    f"**大小**: {img_path.stat().st_size}B\n\n"
                    f"**llava 描述**:\n{description}"
                )
            else:
                return self._resp(f"llava 调用失败: {resp.status_code}")
        except Exception as e:
            return self._resp(f"分析失败: {e}")

    def _list_styles(self) -> Dict:
        return self._resp(
            f"## 🎨 可用风格\n\n"
            + "\n".join(f"• {s}" for s in self.STYLES) +
            f"\n\n## 📐 可用比例\n\n"
            + "\n".join(f"• {k} ({v})" for k, v in self.RATIOS.items())
        )

    def _help(self) -> Dict:
        return self._resp(
            "👁 **视觉助手**\n\n"
            "• 生成 海边日落 动漫风格\n"
            "• 角色立绘 年轻女科学家\n"
            "• 场景图 未来城市夜景\n"
            "• 分镜画面 主角震惊表情 特写\n"
            "• 分析 /path/to/image.png\n"
            "• 风格 查看所有画风"
        )

    def _clean_prompt(self, text: str) -> str:
        for kw in ["生成", "画", "创建", "绘制", "角色立绘", "场景图", "分镜画面", "图片"]:
            text = text.replace(kw, "")
        return text.strip() or "美丽风景"

    def _detect_style(self, text: str) -> str:
        for s in self.STYLES:
            if s in text:
                return s
        return "写实"

    def _detect_ratio(self, text: str) -> str:
        for k in self.RATIOS:
            if k in text:
                return k
        return "方形"

    def _extract_path(self, text: str) -> str:
        m = re.search(r'["\']([^"\']+)["\']|([/\w\-\.]+\.\w{3,4})', text)
        return (m.group(1) or m.group(2)) if m else ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = VisionAgentV4("test")
    print(agent.process("生成 海边日落 动漫风格")["response"][:300])
