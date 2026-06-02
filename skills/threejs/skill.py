"""Three.js 3D 场景生成技能"""

from pathlib import Path
from typing import Dict, Any


class ThreeJSSkill:
    """Three.js 3D 场景生成器"""
    
    name = "threejs"
    description = "生成 Three.js 3D 场景 HTML 文件"
    version = "1.0.0"
    category = "3d"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行 3D 场景生成
        
        Args:
            params: 参数字典
                - shape: 形状 (cube/sphere/cylinder)
                - color: 颜色值 (#RRGGBB 格式)
                - output: 输出路径（可选）
        
        Returns:
            dict: {"success": bool, "result": str} 或 {"success": bool, "error": str}
        """
        shape = params.get('shape', 'cube')
        color = params.get('color', '#ff6600')
        output_path = params.get('output', f"data/output/3d_{shape}.html")
        
        try:
            html = self._generate_html(shape, color)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(html)
            
            return {
                "success": True,
                "result": output_path,
                "message": f"3D 场景已生成: {shape}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_html(self, shape: str, color: str) -> str:
        return f'''<!DOCTYPE html>
<html>
<head><title>ClawsJoy 3D Scene</title>
<style>body{{margin:0;overflow:hidden;}}</style>
<script type="importmap">{{"imports":{{"three":"https://unpkg.com/three@0.128.0/build/three.module.js"}}}}</script>
</head>
<body>
<script type="module">
import * as THREE from 'three';
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111122);
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 5;
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

let geometry;
if("{shape}"==="cube") geometry = new THREE.BoxGeometry(1.5,1.5,1.5);
else geometry = new THREE.SphereGeometry(1,32,32);

const material = new THREE.MeshStandardMaterial({{color:0x{color[1:]}}});
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);

const light = new THREE.DirectionalLight(0xffffff,1);
light.position.set(5,5,5);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));

function animate(){{
    requestAnimationFrame(animate);
    mesh.rotation.x += 0.01;
    mesh.rotation.y += 0.01;
    renderer.render(scene, camera);
}}
animate();
</script>
</body>
</html>'''


skill = ThreeJSSkill()
