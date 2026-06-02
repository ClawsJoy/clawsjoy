"""GPU 安全渲染技能 - Blender GPU 加速"""

import subprocess
from pathlib import Path
from typing import Dict, Any


class GPUSafeRenderSkill:
    """GPU 安全渲染技能"""
    
    name = "gpu_safe_render"
    description = "使用 Blender GPU 渲染 3D 场景"
    version = "1.0.0"
    category = "3d"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行 GPU 渲染
        
        Args:
            params: 参数字典
                - shape: 形状 (cube/sphere)
                - color: 颜色值 (#RRGGBB 格式)
                - output: 输出路径（可选）
        
        Returns:
            dict: {"success": bool, "result": str} 或 {"success": bool, "error": str}
        """
        shape = params.get('shape', 'cube')
        color = params.get('color', '#ff3333')
        output_path = params.get('output', f"data/output/gpu_safe/{shape}_{color[1:]}.png")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        r = int(color[1:3], 16) / 255
        g = int(color[3:5], 16) / 255
        b = int(color[5:7], 16) / 255
        
        script_lines = [
            "import bpy", "import math",
            "bpy.ops.object.select_all(action='SELECT')",
            "bpy.ops.object.delete()",
            f'if "{shape}" == "cube": bpy.ops.mesh.primitive_cube_add(size=2)',
            f'else: bpy.ops.mesh.primitive_uv_sphere_add(radius=1)',
            "mat = bpy.data.materials.new(name='ColorMat')",
            "mat.use_nodes = True",
            f"mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = ({r}, {g}, {b}, 1)",
            "bpy.context.object.active_material = mat",
            "bpy.ops.object.light_add(type='SUN', location=(5,5,5))",
            "bpy.ops.object.camera_add(location=(4,-4,3))",
            "camera = bpy.context.active_object",
            "camera.rotation_euler = (math.radians(60), 0, math.radians(45))",
            "bpy.context.scene.camera = camera",
            "bpy.context.scene.render.resolution_x = 1024",
            "bpy.context.scene.render.resolution_y = 1024",
            f'bpy.context.scene.render.filepath = "{output_path}"',
            "bpy.ops.render.render(write_still=True)"
        ]
        
        try:
            result = subprocess.run(
                ["blender", "-b", "--python-expr", "\n".join(script_lines)],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0 and Path(output_path).exists():
                return {"success": True, "result": output_path}
            return {"success": False, "error": result.stderr[:200] if result.stderr else "渲染失败"}
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = GPUSafeRenderSkill()
