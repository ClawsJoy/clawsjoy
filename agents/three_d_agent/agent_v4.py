#!/usr/bin/env python3
"""three_d_agent v4.0 - 智慧化 3D 处理智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class ThreeDAgentV4(BusinessAgent):
    """智慧化 3D 处理助手"""
    
    name = "three_d_agent_v4"
    description = "智慧化 3D 助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🎨 {self.name} v{self.version} 智慧化启动")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("generate", "model"): (True, 0.85),
            ("render", "scene"): (True, 0.80),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 生成 3D 模型
        if any(kw in user_input for kw in ["生成模型", "创建模型", "3D模型"]):
            return self._generate_model(user_input)
        
        # 渲染场景
        if any(kw in user_input for kw in ["渲染", "场景"]):
            return self._render_scene(user_input)
        
        return self._response(self._smart_fallback(user_input))
    
    def _generate_model(self, user_input: str) -> Dict:
        """生成 3D 模型描述"""
        match = re.search(r'(?:生成模型|创建模型|3D模型)[：:]\s*(.+)', user_input)
        description = match.group(1) if match else user_input.replace("生成模型", "").strip()
        
        if not description:
            return self._response("请描述要生成的模型。\n\n示例：生成模型 一个现代风格的椅子")
        
        prompt = f"""请为以下 3D 模型生成创建指南：

模型描述：{description}

输出内容：
1. 模型类型
2. 推荐软件（Blender/Maya/3ds Max）
3. 创建步骤（3-5步）
4. 材质建议
5. 渲染设置"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"🎨 **3D 模型指南**\n\n{response}",
                metadata={"type": "guide"}
            )
        
        return self._response(self._get_model_template(description))
    
    def _render_scene(self, user_input: str) -> Dict:
        """渲染场景"""
        match = re.search(r'渲染[：:]\s*(.+)', user_input)
        scene = match.group(1) if match else "场景"
        
        prompt = f"""请为以下 3D 场景提供渲染建议：

场景描述：{scene}

输出内容：
1. 推荐渲染器（Cycles/Eevee/V-Ray）
2. 灯光设置
3. 相机角度
4. 材质参数
5. 输出设置"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"🎬 **渲染建议**\n\n{response}",
                metadata={"type": "render"}
            )
        
        return self._response(self._get_render_template(scene))
    
    def _get_model_template(self, description: str) -> str:
        return f"""🎨 **3D 模型创建指南**

模型：{description}

📌 推荐软件：Blender（免费开源）

📝 创建步骤：
1. 收集参考图
2. 建模：使用基础形状搭建结构
3. 细化：添加细节和倒角
4. UV 展开：准备贴图坐标
5. 材质：添加颜色和纹理

🎨 材质建议：
- 主体：金属/塑料
- 细节：粗糙度贴图
- 高光：镜面反射

💡 提示：可在 Blender 中使用插件加速流程"""
    
    def _get_render_template(self, scene: str) -> str:
        return f"""🎬 **渲染建议**

场景：{scene}

🖥️ 推荐渲染器：Cycles（高质量）

💡 灯光设置：
- 主光：三点布光法
- 补光：柔光箱
- 背光：轮廓光

🎥 相机：
- 焦距：50mm（标准视角）
- 光圈：f/2.8（浅景深）
- 角度：平视略带俯视

⚙️ 输出：
- 分辨率：1920x1080
- 采样：512
- 格式：PNG"""
    
