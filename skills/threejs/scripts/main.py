#!/usr/bin/env python3
"""Three.js 3D 场景生成"""

import json


class ThreeJSSkill:
    name = "threejs"
    description = "Three.js 3D 场景生成"
    version = "1.0.0"

    def execute(self, params):
        scene_type = params.get("scene_type", "basic")
        objects = params.get("objects", [])

        # 生成 Three.js HTML
        html = self._generate_html(scene_type, objects)

        return {
            "success": True,
            "code": html,
            "scene_type": scene_type,
            "objects": objects,
        }

    def _generate_html(self, scene_type, objects):
        """生成 Three.js HTML"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Three.js Scene</title>
    <style>
        body {{ margin: 0; overflow: hidden; }}
        #info {{
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            background: rgba(0,0,0,0.6);
            padding: 10px;
            border-radius: 5px;
            font-family: Arial;
            pointer-events: none;
            z-index: 100;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>3D Scene - {scene_type}</h3>
        <p>鼠标拖拽旋转视角 | 右键平移 | 滚轮缩放</p>
    </div>
    <script type="importmap">
        {{
            "imports": {{
                "three": "https://unpkg.com/three@0.128.0/build/three.module.js",
                "three/addons/": "https://unpkg.com/three@0.128.0/examples/jsm/"
            }}
        }}
    </script>
    <script type="module">
        import * as THREE from 'three';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
        
        // 场景
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x111122);
        scene.fog = new THREE.FogExp2(0x111122, 0.008);
        
        // 相机
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(5, 5, 10);
        camera.lookAt(0, 0, 0);
        
        // 渲染器
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);
        
        // 控制器
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.screenSpacePanning = true;
        
        // 辅助元素
        const gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0x444444);
        scene.add(gridHelper);
        
        const axesHelper = new THREE.AxesHelper(5);
        scene.add(axesHelper);
        
        // 环境光
        const ambientLight = new THREE.AmbientLight(0x404040);
        scene.add(ambientLight);
        
        // 主光源
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        scene.add(directionalLight);
        
        // 背光
        const backLight = new THREE.DirectionalLight(0x444466, 0.5);
        backLight.position.set(-5, 0, -5);
        scene.add(backLight);
        
        // 物体
        {self._generate_objects(objects)}
        
        // 动画
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();
        
        // 窗口适配
        window.addEventListener('resize', onWindowResize, false);
        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}
    </script>
</body>
</html>"""

    def _generate_objects(self, objects):
        code = ""
        for obj in objects:
            if obj == "cube":
                code += """
        // 立方体
        const cubeGeometry = new THREE.BoxGeometry(1, 1, 1);
        const cubeMaterial = new THREE.MeshStandardMaterial({ color: 0xff6600, roughness: 0.3, metalness: 0.1 });
        const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
        cube.position.set(2, 0.5, 0);
        cube.castShadow = true;
        cube.receiveShadow = true;
        scene.add(cube);
"""
            elif obj == "sphere":
                code += """
        // 球体
        const sphereGeometry = new THREE.SphereGeometry(0.8, 64, 64);
        const sphereMaterial = new THREE.MeshStandardMaterial({ color: 0x44aa88, roughness: 0.2, metalness: 0.8 });
        const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
        sphere.position.set(-2, 0.8, 1);
        sphere.castShadow = true;
        scene.add(sphere);
"""
        return code


def execute(params):
    skill = ThreeJSSkill()
    return skill.execute(params)


if __name__ == "__main__":
    result = execute({"scene_type": "basic", "objects": ["cube", "sphere"]})
    print(result.get("code", "")[:500])
