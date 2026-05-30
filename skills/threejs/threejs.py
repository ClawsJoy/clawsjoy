#!/usr/bin/env python3
"""Threejs - Threejs 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import json

class ThreeJSGenerator:
    """3D 场景生成器"""
    
    def execute(self, params):
        """生成 3D 场景"""
        scene_type = params.get('type', 'cube')
        color = params.get('color', '#00ff00')
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>3D Scene - ClawsJoy</title>
    <style>
        body {{ margin: 0; overflow: hidden; font-family: Arial, sans-serif; }}
        .info {{ position: absolute; top: 20px; left: 20px; color: white; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 5px; z-index: 100; }}
    </style>
    <script type="importmap">
        {{
            "imports": {{
                "three": "https://unpkg.com/three@0.128.0/build/three.module.js"
            }}
        }}
    </script>
</head>
<body>
    <div class="info">
        <h3>ClawsJoy 3D 场景</h3>
        <p>类型: {scene_type} | 颜色: {color}</p>
    </div>
    <script type="module">
        import * as THREE from 'three';
        
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x111122);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 5;
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        let geometry;
        switch('{scene_type}') {{
            case 'cube':
                geometry = new THREE.BoxGeometry(1, 1, 1);
                break;
            case 'sphere':
                geometry = new THREE.SphereGeometry(0.8, 32, 32);
                break;
            case 'torus':
                geometry = new THREE.TorusGeometry(0.8, 0.3, 32, 100);
                break;
            default:
                geometry = new THREE.BoxGeometry(1, 1, 1);
        }}
        
        const material = new THREE.MeshStandardMaterial({{ color: '{color}', roughness: 0.3, metalness: 0.7 }});
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);
        
        const ambientLight = new THREE.AmbientLight(0x404040);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(1, 2, 1);
        scene.add(directionalLight);
        
        function animate() {{
            requestAnimationFrame(animate);
            mesh.rotation.x += 0.005;
            mesh.rotation.y += 0.01;
            renderer.render(scene, camera);
        }}
        animate();
        
        window.addEventListener('resize', onWindowResize, false);
        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}
    </script>
</body>
</html>'''
        
        return {"html": html, "success": True, "type": scene_type}


skill = ThreeJSGenerator()
