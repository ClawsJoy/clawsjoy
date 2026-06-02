"""360度全景渲染技能"""

from pathlib import Path
from typing import Dict, Any


class PanoramaSkill:
    """360度全景渲染技能"""
    
    name = "panorama"
    description = "生成 360 度全景查看器 HTML"
    version = "1.0.0"
    category = "3d"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行全景生成
        
        Args:
            params: 参数字典
                - action: 操作类型 (view/render)
                - image: 全景图路径（可选）
                - output: 输出路径（可选）
        
        Returns:
            dict: {"success": bool, "result": str} 或 {"success": bool, "error": str}
        """
        action = params.get('action', 'view')
        image_path = params.get('image', '')
        output_path = params.get('output', 'data/output/panorama/viewer.html')
        
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            if action == 'view':
                html = self._generate_viewer(image_path)
                with open(output_path, 'w') as f:
                    f.write(html)
                return {"success": True, "result": output_path}
            else:
                return {"success": False, "error": f"未知操作: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_viewer(self, image_path: str) -> str:
        if not image_path:
            image_path = "https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg"
        
        return f'''<!DOCTYPE html>
<html>
<head><title>360° Panorama</title>
<style>body{{margin:0;overflow:hidden;}}</style>
<script type="importmap">{{"imports":{{"three":"https://unpkg.com/three@0.128.0/build/three.module.js"}}}}</script>
</head>
<body>
<script type="module">
import * as THREE from 'three';
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth,window.innerHeight);
document.body.appendChild(renderer.domElement);

const texture = new THREE.TextureLoader().load('{image_path}');
const geometry = new THREE.SphereGeometry(500,64,64);
const material = new THREE.MeshBasicMaterial({{map:texture,side:THREE.BackSide}});
const sphere = new THREE.Mesh(geometry,material);
scene.add(sphere);

let mouseX=0,targetX=0;
document.addEventListener('mousemove',(e)=>{{
    mouseX = (e.clientX/window.innerWidth)*2-1;
    targetX = mouseX*Math.PI;
}});
function animate(){{
    requestAnimationFrame(animate);
    sphere.rotation.y += (targetX-sphere.rotation.y)*0.05;
    renderer.render(scene,camera);
}}
animate();
</script>
</body>
</html>'''


skill = PanoramaSkill()
