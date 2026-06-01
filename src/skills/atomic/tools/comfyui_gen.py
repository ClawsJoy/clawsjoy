#!/usr/bin/env python3
"""Comfyui Gen - Comfyui Gen 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import requests
import json
import time
import uuid
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

class ComfyUIGenSkill:
    name = "comfyui_gen"
    description = "通过 ComfyUI API 自动生成图像"
    version = "1.0.0"
    category = "tools"
    
    def __init__(self):
        self.comfyui_url = f"http://{smart_config.HOST}:{smart_config.get_port("comfyui")}"
    
    def execute(self, params):
        prompt = params.get("prompt", "")
        if not prompt:
            return {"success": False, "error": "需要提供提示词"}
        
        # 检查 ComfyUI 是否运行
        if not self._is_comfyui_running():
            return {
                "success": False, 
                "error": "ComfyUI 未运行，请先启动: cd tools/ComfyUI && python main.py",
                "fallback": self._fallback_generate(prompt)
            }
        
        # 调用 ComfyUI API
        return self._generate_with_comfyui(prompt)
    
    def _is_comfyui_running(self):
        try:
            resp = requests.get(f"{self.comfyui_url}/system_stats", timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def _generate_with_comfyui(self, prompt):
        """通过 ComfyUI API 生成"""
        # 基础工作流配置
        workflow = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 42,
                    "steps": 20,
                    "cfg": 7,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 512, "height": 512, "batch_size": 1}
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["4", 1]}
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "", "clip": ["4", 1]}
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "ClawsJoy", "images": ["8", 0]}
            }
        }
        
        try:
            # 提交任务
            resp = requests.post(
                f"{self.comfyui_url}/prompt",
                json={"prompt": workflow, "client_id": str(uuid.uuid4())},
                timeout=30
            )
            data = resp.json()
            prompt_id = data.get('prompt_id')
            
            if not prompt_id:
                return {"success": False, "error": "提交失败"}
            
            # 等待完成
            for _ in range(30):
                time.sleep(1)
                resp = requests.get(f"{self.comfyui_url}/history/{prompt_id}")
                if resp.status_code == 200:
                    history = resp.json()
                    if prompt_id in history:
                        outputs = history[prompt_id].get('outputs', {})
                        for node_id, node_output in outputs.items():
                            if 'images' in node_output:
                                image = node_output['images'][0]
                                return {
                                    "success": True,
                                    "image_path": f"output/comfyui_{image['filename']}",
                                    "source": "comfyui",
                                    "message": f"图像已生成"
                                }
            return {"success": False, "error": "超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _fallback_generate(self, prompt):
        """降级方案：使用内置图像生成"""
        from src.skills.atomic.tools.image_gen import skill
        return skill.execute({"prompt": prompt})

skill = ComfyUIGenSkill()
