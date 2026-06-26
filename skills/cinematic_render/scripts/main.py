#!/usr/bin/env python3
"""电影级渲染技能 - 高质量 Cycles 渲染"""

import math
import subprocess
from pathlib import Path
from typing import Any, Dict


class CinematicRenderSkill:
    """电影级渲染技能"""

    name = "cinematic_render"
    description = "电影级高质量渲染"
    version = "1.0.0"
    category = "3d"

    def __init__(self):
        self.output_dir = Path("data/output/cinematic")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        shape = params.get("shape", "sphere")
        quality = params.get("quality", "high")
        output_path = self.output_dir / f"{shape}_{quality}.png"

        quality_settings = {
            "high": {"samples": 64, "resolution": 1024, "threads": 4},
            "cinema": {"samples": 128, "resolution": 1920, "threads": 4},
            "ultra": {"samples": 256, "resolution": 3840, "threads": 2},
        }

        settings = quality_settings.get(quality, quality_settings["high"])

        script = self._generate_script(shape, settings, str(output_path))
        script_file = self.output_dir / "render.py"
        script_file.write_text(script)

        try:
            result = subprocess.run(
                ["blender", "-b", "--python", str(script_file)],
                capture_output=True,
                text=True,
                timeout=600,
            )
            script_file.unlink()

            if result.returncode == 0 and output_path.exists():
                return {
                    "success": True,
                    "message": f"电影级渲染完成: {shape} ({quality})",
                    "output": str(output_path),
                    "size": output_path.stat().st_size,
                    "quality": quality,
                    "samples": settings["samples"],
                }
            return {"success": False, "error": result.stderr[:500]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_script(self, shape: str, settings: dict, output_path: str) -> str:
        samples = settings["samples"]
        resolution = settings["resolution"]
        threads = settings["threads"]

        return f"""
import bpy
import math

# 清空场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建物体
if "{shape}" == "sphere":
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, segments=64)
else:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, segments=64)

bpy.ops.object.shade_smooth()

# 金属材质
mat = bpy.data.materials.new(name="CinematicMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# 清除默认节点
for node in nodes:
    nodes.remove(node)

# 创建材质节点
output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Metallic'].default_value = 0.95
bsdf.inputs['Roughness'].default_value = 0.15
bsdf.inputs['Base Color'].default_value = (0.85, 0.55, 0.35, 1.0)

links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
bpy.context.object.active_material = mat

# 灯光
bpy.ops.object.light_add(type='SUN', location=(5, 5, 8))
key = bpy.context.active_object
key.data.energy = 3.5

bpy.ops.object.light_add(type='AREA', location=(-4, 3, 2))
fill = bpy.context.active_object
fill.data.energy = 1.2

bpy.ops.object.light_add(type='SUN', location=(0, -6, 4))
back = bpy.context.active_object
back.data.energy = 2.0

# 环境
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.05, 0.05, 0.08, 1.0)
    bg.inputs['Strength'].default_value = 0.5

# 相机
bpy.ops.object.camera_add(location=(4.5, -5, 3.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(55), 0, math.radians(42))
bpy.context.scene.camera = camera

# 渲染设置
bpy.context.scene.render.resolution_x = {resolution}
bpy.context.scene.render.resolution_y = {resolution}
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = {samples}
bpy.context.scene.cycles.use_adaptive_sampling = True
bpy.context.scene.cycles.tile_size = 512
bpy.context.scene.render.threads_mode = 'FIXED'
bpy.context.scene.render.threads = {threads}
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.filepath = "{output_path}"

bpy.ops.render.render(write_still=True)
print("渲染完成")
"""


skill = CinematicRenderSkill()
