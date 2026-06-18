#!/usr/bin/env python3
"""VisionAgent v4.2 - 精简稳定版（视觉助手）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class VisionAgentV4(BusinessAgent):
    """视觉 Agent - 精简稳定版"""

    name = "vision_agent_v4"
    description = "智慧视觉助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.output_dir = Path(f"data/vision/{user_id}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"👁 VisionAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        
        if any(kw in t for kw in ["生成", "画", "创建"]):
            return self._generate_image(user_input)
        
        if any(kw in t for kw in ["分析", "识别", "描述"]):
            return self._analyze_image(user_input)
        
        return self._resp("👁 我是视觉助手。输入「生成 风景画」或「分析 图片路径」")

    # ================================================================
    #  生成图像
    # ================================================================

    def _generate_image(self, user_input: str) -> Dict:
        prompt = user_input
        for kw in ["生成", "画", "创建", "图片"]:
            prompt = prompt.replace(kw, "").strip()
        if not prompt:
            prompt = "美丽的风景"
        
        return self._resp(f"""
🎨 图像生成请求

📝 提示词: {prompt}
📁 输出: {self.output_dir}

💡 提示: 当前为模拟模式，可接入 Stable Diffusion 生成实际图像
""")

    # ================================================================
    #  分析图像
    # ================================================================

    def _analyze_image(self, user_input: str) -> Dict:
        return self._resp("""
🖼 图像分析功能

支持:
1. 图像描述
2. 物体识别
3. 文字提取 (OCR)

请提供图像路径或 URL。
""")

    # ================================================================
    #  辅助方法
    # ================================================================

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = VisionAgentV4("test")
    print(agent.process("生成 海边日落")["response"])   
