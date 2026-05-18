#!/usr/bin/env python3
"""AI Image Generator - 配置驱动版"""

import sys
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'core'))

from lib.config_loader import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SKILL_INFO = {
    "name": "ai-image-gen",
    "version": "1.3.0",
    "author": "ClawsJoy",
    "tags": ["image", "generation", "comfyui", "config-driven"]
}


def _get_comfy_config() -> Dict[str, Any]:
    """从配置获取 ComfyUI 配置"""
    return {
        "host": config.get('ports.image_gen.comfyui.host', '127.0.0.1'),
        "port": config.get('ports.image_gen.comfyui.port', 8188),
        "timeout": config.get('ports.image_gen.comfyui.timeout', 60),
        "api_path": config.get('ports.image_gen.comfyui.api_path', '/prompt')
    }


def _get_generation_config() -> Dict[str, Any]:
    """从配置获取生成参数"""
    return {
        "width": config.get('models.generation.default_width', 512),
        "height": config.get('models.generation.default_height', 768),
        "steps": config.get('models.generation.default_steps', 20),
        "cfg": config.get('models.generation.default_cfg', 7),
        "sampler": config.get('models.generation.default_sampler', 'euler'),
        "scheduler": config.get('models.generation.default_scheduler', 'normal'),
        "model": config.get('models.image_models.sd15.name', 'v1-5-pruned-emaonly.safetensors')
    }


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """执行图像生成 - 配置驱动"""
    logger.info(f"AI Image Generator (config-driven) called")
    
    # 测试/验证模式
    if params.get('test') or params.get('validate'):
        comfy_config = _get_comfy_config()
        gen_config = _get_generation_config()
        return {
            "success": True,
            "result": {
                "message": "AI Image Generator is ready",
                "mode": "config-driven",
                "comfy_url": f"http://{comfy_config['host']}:{comfy_config['port']}",
                "default_model": gen_config['model'],
                "default_size": f"{gen_config['width']}x{gen_config['height']}"
            }
        }
    
    # 获取提示词
    prompt = params.get('prompt', params.get('text', ''))
    if not prompt:
        return {"success": False, "error": "Missing 'prompt' parameter"}
    
    # 从配置获取参数（支持参数覆盖）
    gen_config = _get_generation_config()
    comfy_config = _get_comfy_config()
    
    width = params.get('width', gen_config['width'])
    height = params.get('height', gen_config['height'])
    steps = params.get('steps', gen_config['steps'])
    cfg = params.get('cfg_scale', gen_config['cfg'])
    
    comfy_url = f"http://{comfy_config['host']}:{comfy_config['port']}"
    
    try:
        # 构建 ComfyUI 工作流（使用配置中的值）
        workflow = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": int(time.time()),
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": gen_config['sampler'],
                    "scheduler": gen_config['scheduler'],
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": gen_config['model']}
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1}
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["4", 1]}
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "bad quality, blurry, ugly", "clip": ["4", 1]}
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "clawsjoy_character", "images": ["8", 0]}
            }
        }
        
        # 发送请求
        resp = requests.post(
            f"{comfy_url}{comfy_config['api_path']}",
            json={"prompt": workflow},
            timeout=comfy_config['timeout']
        )
        
        if resp.status_code == 200:
            result = resp.json()
            return {
                "success": True,
                "result": {
                    "prompt_id": result.get('prompt_id'),
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "model": gen_config['model'],
                    "mode": "config-driven",
                    "message": f"图像生成任务已提交"
                }
            }
        else:
            return {"success": False, "error": f"ComfyUI 错误: {resp.text[:200]}"}
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"ComfyUI 未启动 (http://{comfy_config['host']}:{comfy_config['port']})",
            "hint": "请启动 ComfyUI 服务"
        }
    except Exception as e:
        logger.error(f"生成失败: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    test_result = execute({"test": True})
    print(json.dumps(test_result, indent=2, ensure_ascii=False))
