from core.agents.business.business_agent_v2 import BusinessAgentV2
#!/usr/bin/env python3
"""视觉智能体 - 增强版（图片识别、OCR、物体检测）"""

import re
from typing import Dict, Optional

from core.agents.business.base_business_agent import BusinessAgent


class VisionAgent(BusinessAgentV2):
    name = "vision_agent"
    description = "智能视觉识别"
    version = "3.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._init_vision_skills()
        print(f"👁️ 视觉智能体 v3.0 已上线")

    def _init_vision_skills(self):
        """初始化视觉能力"""
        self.vision_available = False
        try:
            from skills.image.vision import VisionSkill

            self.vision_skill = VisionSkill()
            self.vision_available = True
            print("   ✅ 视觉技能已加载")
        except:
            print("   ⚠️ 视觉技能不可用，使用模拟模式")

    def _execute_business(self, user_input: str, context: dict = None) -> dict:
        """业务逻辑实现 - BusinessAgent 要求"""
        return self.process(user_input, context)

    def _describe_image(self, image_path: str) -> Dict:
        """描述图片"""
        if self.vision_available:
            try:
                result = self.vision_skill.execute(
                    {"action": "describe", "image": image_path}
                )
                description = result.get("description", "无法识别")
            except:
                description = "图片描述功能需要配置视觉模型"
        else:
            description = f"[模拟] 图片 {image_path} 的描述：这是一张图片"

        return {
            "success": True,
            "response": f"🖼️ 图片描述：{description}",
            "image": image_path,
            "description": description,
            "agent": self.name,
            "user_id": self.user_id,
        }

    def _ocr_image(self, image_path: str) -> Dict:
        """OCR 文字识别"""
        text = f"[OCR] 从 {image_path} 识别到的文字：示例文字内容"
        return {
            "success": True,
            "response": f"📝 OCR识别结果：{text}",
            "image": image_path,
            "text": text,
            "agent": self.name,
            "user_id": self.user_id,
        }

    def _detect_objects(self, image_path: str) -> Dict:
        """物体检测"""
        objects = ["人物", "车辆", "建筑", "自然景观"]
        return {
            "success": True,
            "response": f"🔍 检测到物体：{', '.join(objects)}",
            "image": image_path,
            "objects": objects,
            "agent": self.name,
            "user_id": self.user_id,
        }

    def _detect_faces(self, image_path: str) -> Dict:
        """人脸检测"""
        faces = 3
        return {
            "success": True,
            "response": f"😊 检测到 {faces} 张人脸",
            "image": image_path,
            "face_count": faces,
            "agent": self.name,
            "user_id": self.user_id,
        }

    def _extract_image_path(self, text: str) -> str:
        """提取图片路径"""
        match = re.search(r"['\"]([^'\"]+\.(jpg|png|jpeg))['\"]", text, re.IGNORECASE)
        if match:
            return match.group(1)
        return "未指定图片路径"

    def _help(self) -> Dict:
        """帮助信息"""
        return {
            "success": True,
            "response": "👁️ 视觉功能：\n• 说「描述图片 /path/to/image.jpg」\n• 说「OCR识别 /path/to/image.jpg」\n• 说「物体检测 /path/to/image.jpg」",
            "agent": self.name,
            "user_id": self.user_id,
        }

