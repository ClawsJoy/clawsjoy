"""视觉 Agent - 图片识别和描述生成"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent


class VisionAgent(SmartAgent):
    """视觉识别 Agent"""

    name = "vision_agent"
    description = "图片识别和描述生成"
    version = "1.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._init_vision_skill()
        print("👁️ VisionAgent 初始化完成")

    def _init_vision_skill(self):
        """初始化视觉技能"""
        try:
            from skills.image.vision import VisionSkill
            self.vision_skill = VisionSkill()
            print("   ✅ 视觉技能已加载 (moondream)")
        except Exception as e:
            print(f"   ❌ 技能加载失败: {e}")
            self.vision_skill = None

    def describe_image(self, image_path: str, prompt: str = "描述这张图片的内容") -> Dict:
        """识别图片并生成描述"""
        if not self.vision_skill:
            return {
                "success": False,
                "error": "Vision skill not available",
                "image_path": image_path
            }

        try:
            result = self.vision_skill.execute({
                "image_path": image_path,
                "prompt": prompt
            })

            return {
                "success": result.get("success", False),
                "description": result.get("description", result.get("result", "")),
                "image_path": image_path,
                "error": result.get("error")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }

    def describe_image_with_retry(self, image_path: str, prompt: str = None, max_retries: int = 3) -> Dict:
        """带重试的图片识别"""
        import time
        last_error = None

        for attempt in range(max_retries):
            result = self.describe_image(image_path, prompt)

            if result.get('success'):
                if attempt > 0:
                    print(f"   ✅ 重试第 {attempt + 1} 次成功")
                return result

            last_error = result.get('error')
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"   ⚠️ 识别失败，{wait_time}秒后重试 ({attempt + 1}/{max_retries})")
                time.sleep(wait_time)

        return {
            "success": False,
            "error": f"重试{max_retries}次后失败: {last_error}",
            "image_path": image_path
        }

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理请求"""
        return self.describe_image(user_input)


# 全局实例
vision_agent = VisionAgent()
