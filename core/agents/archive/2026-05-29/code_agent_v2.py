from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""CODE Agent v2.0 - 代码生成、审查、执行"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Optional

from core.lib.smart_adapter import smart_adapter
from core.lib.threejs_knowledge import threejs_kb


class CodeAgentV2:
    """CODE Agent - 智能编程助手"""
    
    VERSION = "2.0.0"
    
    def __init__(self):
        self.code_history = []
        self.templates = self._load_templates()
        print(f"🤖 CODE Agent v{self.VERSION} 已启动")
    
    def _load_templates(self):
        """加载代码模板"""
        return {
            "threejs_cockpit": '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ClawsJoy 3D座舱</title>
    <style>
        body { margin: 0; overflow: hidden; background: #0a0a1a; }
        #info { position: absolute; bottom: 20px; left: 20px; color: #00f3ff; font-family: monospace; }
    </style>
</head>
<body>
    <div id="info">ClawsJoy 3D座舱 | 拖动视角查看</div>
    <script type="importmap">
        { "imports": { "three": "https://unpkg.com/three@0.128.0/build/three.module.js" } }
    </script>
    <script type="module">
        import * as THREE from 'three';
        
        // 场景
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0a1a);
        scene.fog = new THREE.FogExp2(0x0a0a1a, 0.008);
        
        // 相机
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2, 8);
        camera.lookAt(0, 0, 0);
        
        // 渲染器
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);
        
        // 星空粒子
        const starGeometry = new THREE.BufferGeometry();
        const starCount = 2000;
        const starPositions = new Float32Array(starCount * 3);
        for (let i = 0; i < starCount; i++) {
            starPositions[i*3] = (Math.random() - 0.5) * 200;
            starPositions[i*3+1] = (Math.random() - 0.5) * 100;
            starPositions[i*3+2] = (Math.random() - 0.5) * 100 - 50;
        }
        starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
        const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.2 });
        const stars = new THREE.Points(starGeometry, starMaterial);
        scene.add(stars);
        
        // 弧形穹顶
        const domeGeometry = new THREE.SphereGeometry(3.5, 32, 32, 0, Math.PI * 2, 0, Math.PI / 3);
        const domeMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x00f3ff, 
            emissive: 0x003344,
            transparent: true, 
            opacity: 0.15,
            wireframe: false
        });
        const dome = new THREE.Mesh(domeGeometry, domeMaterial);
        dome.position.y = 1.5;
        scene.add(dome);
        
        // 环形光带
        const ringGeometry = new THREE.TorusGeometry(3.8, 0.05, 64, 200);
        const ringMaterial = new THREE.MeshStandardMaterial({ color: 0x00f3ff, emissive: 0x00f3ff });
        const ring = new THREE.Mesh(ringGeometry, ringMaterial);
        ring.rotation.x = Math.PI / 2;
        ring.position.y = 0.5;
        scene.add(ring);
        
        // 左右舱壁
        const wallMaterial = new THREE.MeshStandardMaterial({ color: 0x112233, emissive: 0x003344, transparent: true, opacity: 0.7 });
        const leftWall = new THREE.Mesh(new THREE.BoxGeometry(2, 3, 0.2), wallMaterial);
        leftWall.position.set(-3.5, 1, -1);
        leftWall.rotation.y = 0.3;
        scene.add(leftWall);
        
        const rightWall = new THREE.Mesh(new THREE.BoxGeometry(2, 3, 0.2), wallMaterial);
        rightWall.position.set(3.5, 1, -1);
        rightWall.rotation.y = -0.3;
        scene.add(rightWall);
        
        // 中央巨幕
        const screenGeometry = new THREE.PlaneGeometry(5, 2.8);
        const screenMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x00aaff, 
            emissive: 0x004466,
            side: THREE.DoubleSide 
        });
        const screen = new THREE.Mesh(screenGeometry, screenMaterial);
        screen.position.set(0, 1.2, -1.5);
        scene.add(screen);
        
        // 灯光
        const ambientLight = new THREE.AmbientLight(0x222222);
        scene.add(ambientLight);
        const pointLight = new THREE.PointLight(0x00f3ff, 0.5);
        pointLight.position.set(0, 3, 2);
        scene.add(pointLight);
        
        // 全息扫描线
        const scanPlane = new THREE.Mesh(
            new THREE.PlaneGeometry(5, 2.8),
            new THREE.MeshBasicMaterial({ color: 0x00f3ff, transparent: true, opacity: 0.3, side: THREE.DoubleSide })
        );
        scanPlane.position.set(0, 1.2, -1.4);
        scene.add(scanPlane);
        
        let scanOffset = 0;
        
        // 动画
        function animate() {
            requestAnimationFrame(animate);
            
            stars.rotation.y += 0.0005;
            stars.rotation.x += 0.0003;
            ring.rotation.z += 0.005;
            
            scanOffset += 0.02;
            scanPlane.position.y = 1.2 + Math.sin(scanOffset) * 1.2;
            
            renderer.render(scene, camera);
        }
        animate();
        
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
'''
        }
    
    def generate_code(self, request: str) -> Dict:
        """根据需求生成代码"""
        
        # 1. 检索知识库
        knowledge = threejs_kb.retrieve(request, top_k=3)
        
        # 2. 识别代码类型
        code_type = self._detect_code_type(request)
        
        # 3. 生成代码
        if "three.js" in request.lower() or "3d" in request.lower() or "座舱" in request:
            code = self._generate_threejs(request, knowledge)
        else:
            code = self._generate_general(request)
        
        # 4. 保存到历史
        self.code_history.append({
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "code": code[:500],
            "type": code_type
        })
        
        return {
            "success": True,
            "code": code,
            "type": code_type,
            "suggestions": self._get_suggestions(code_type)
        }
    
    def _detect_code_type(self, request: str) -> str:
        """检测代码类型"""
        if "three" in request.lower() or "3d" in request.lower():
            return "threejs"
        if "html" in request.lower():
            return "html"
        if "python" in request.lower():
            return "python"
        if "css" in request.lower():
            return "css"
        return "general"
    
    def _generate_threejs(self, request: str, knowledge: List) -> str:
        """生成 Three.js 代码"""
        # 使用模板生成
        template = self.templates.get("threejs_cockpit")
        
        # 根据知识库定制
        for k in knowledge:
            if "曲面" in k.get('topic', ''):
                template = template.replace("opacity: 0.15", "opacity: 0.25")
        
        return template
    
    def _generate_general(self, request: str) -> str:
        """生成通用代码"""
        prompt = f"请根据以下需求生成代码：\n{request}\n只返回代码，不要解释。"
        response = smart_adapter.generate(prompt, auto_select=True)
        return response
    
    def _get_suggestions(self, code_type: str) -> List[str]:
        """获取优化建议"""
        suggestions = {
            "threejs": [
                "可以调整相机位置获得更好的视角",
                "添加轨道控制让用户交互",
                "增加粒子系统增强视觉效果"
            ],
            "html": [
                "添加响应式设计",
                "优化移动端适配"
            ],
            "python": [
                "添加错误处理",
                "添加类型注解"
            ]
        }
        return suggestions.get(code_type, ["代码已生成，请审核"])
    
    def review_code(self, code: str) -> Dict:
        """代码审查"""
        issues = []
        
        # 检查常见问题
        if "TODO" in code:
            issues.append("发现 TODO 注释，请确认是否完成")
        if "console.log" in code and "production" in code.lower():
            issues.append("生产环境建议移除 console.log")
        if "var " in code:
            issues.append("建议使用 let/const 代替 var")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": self._get_suggestions(self._detect_code_type(code))
        }
    
    def execute_code(self, code: str, language: str = "html") -> Dict:
        """在沙箱中执行代码"""
        if language == "html":
            # 保存为临时 HTML 文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            return {
                "success": True,
                "file_path": temp_path,
                "message": f"代码已保存到 {temp_path}，可在浏览器中打开"
            }
        
        return {"success": False, "message": "不支持的执行类型"}


# 全局实例
code_agent = CodeAgentV2()
