"""OpenGL 本地 3D 渲染技能"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any


class OpenGLRenderSkill:
    """OpenGL 本地渲染技能"""
    
    name = "opengl_render"
    description = "使用 OpenGL 本地渲染 3D 场景"
    version = "1.0.0"
    category = "3d"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行 OpenGL 渲染
        
        Args:
            params: 参数字典
                - shape: 形状 (cube/sphere)
                - output: 输出路径（可选）
        
        Returns:
            dict: {"success": bool, "result": str} 或 {"success": bool, "error": str}
        """
        shape = params.get('shape', 'cube')
        output_path = params.get('output', f"data/output/opengl/opengl_{shape}.png")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        script = self._generate_script(shape, str(output_path))
        script_file = Path(output_path).parent / "render.py"
        script_file.write_text(script)
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_file)],
                capture_output=True, text=True, timeout=10
            )
            script_file.unlink()
            
            if result.returncode == 0 and Path(output_path).exists():
                return {"success": True, "result": output_path}
            return {"success": False, "error": result.stderr[:300] if result.stderr else "渲染失败"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_script(self, shape: str, output_path: str) -> str:
        return f'''#!/usr/bin/env python3
import pygame
from pygame.locals import *
from OpenGL.GL import *
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

pygame.init()
screen = pygame.display.set_mode((800,600), DOUBLEBUF|OPENGL)
glClearColor(0.1,0.1,0.2,1.0)
glEnable(GL_DEPTH_TEST)

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glFrustum(-1,1,-1,1,1.5,20.0)
glTranslatef(0,0,-5)

glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

glRotatef(30,1,1,0)
glBegin(GL_QUADS)
glColor3f(1,0.2,0.2)
glVertex3f(-1,-1,1);glVertex3f(1,-1,1);glVertex3f(1,1,1);glVertex3f(-1,1,1)
glColor3f(0.2,1,0.2)
glVertex3f(1,-1,1);glVertex3f(1,-1,-1);glVertex3f(1,1,-1);glVertex3f(1,1,1)
glColor3f(0.2,0.2,1)
glVertex3f(-1,1,1);glVertex3f(1,1,1);glVertex3f(1,1,-1);glVertex3f(-1,1,-1)
glEnd()

pygame.display.flip()
pygame.image.save(screen, "{output_path}")
pygame.quit()
'''


skill = OpenGLRenderSkill()
