from lib.smart_config import smart_config
#!/usr/bin/env python3
"""
SD 1.5 文生图原子技能 - ClawsJoy OpenClaw 标准接口
所有路径通过环境变量或配置文件读取，无硬编码
"""

import sys
import json
import argparse
import time
import os
from pathlib import Path
from diffusers import StableDiffusionPipeline
import torch

def get_config():
    """从环境变量或默认值获取配置"""
    return {
        "model_path": os.environ.get('CLAWSJOY_SD15_PATH', 'str(smart_config.ROOT)/models/sd15'),
        "output_dir": os.environ.get('CLAWSJOY_OUTPUT_DIR', 'str(smart_config.ROOT)/output'),
        "default_steps": int(os.environ.get('CLAWSJOY_SD15_STEPS', '20')),
        "default_width": int(os.environ.get('CLAWSJOY_SD15_WIDTH', '512')),
        "default_height": int(os.environ.get('CLAWSJOY_SD15_HEIGHT', '512')),
        "default_cfg": float(os.environ.get('CLAWSJOY_SD15_CFG', '7.0')),
        "default_negative": os.environ.get('CLAWSJOY_SD15_NEGATIVE', 'low quality, blurry')
    }

def main():
    config = get_config()
    
    parser = argparse.ArgumentParser(description='SD 1.5 文生图原子技能')
    parser.add_argument('--prompt', '-p', required=True, help='图像描述提示词')
    parser.add_argument('--negative_prompt', '-n', default=config['default_negative'], help='负面提示词')
    parser.add_argument('--steps', '-s', type=int, default=config['default_steps'], help='推理步数')
    parser.add_argument('--width', '-W', type=int, default=config['default_width'], help='图像宽度')
    parser.add_argument('--height', '-H', type=int, default=config['default_height'], help='图像高度')
    parser.add_argument('--cfg', '-c', type=float, default=config['default_cfg'], help='引导系数')
    parser.add_argument('--json', '-j', action='store_true', help='JSON 格式输出')
    parser.add_argument('--output', '-o', default=None, help='输出路径')
    
    args = parser.parse_args()
    
    # 加载模型
    print(f"加载模型: {config['model_path']}", file=sys.stderr)
    pipe = StableDiffusionPipeline.from_pretrained(
        config['model_path'],
        torch_dtype=torch.float16
    )
    pipe.enable_model_cpu_offload()
    print("模型加载完成", file=sys.stderr)
    
    # 生成图片
    start = time.time()
    image = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        num_inference_steps=args.steps,
        height=args.height,
        width=args.width,
        guidance_scale=args.cfg
    ).images[0]
    
    elapsed = time.time() - start
    
    # 保存图片
    if args.output is None:
        os.makedirs(config['output_dir'], exist_ok=True)
        output_path = os.path.join(config['output_dir'], f"sd15_{int(time.time())}.png")
    else:
        output_path = args.output
    
    image.save(output_path)
    
    result = {
        "success": True,
        "image_path": output_path,
        "elapsed_time": round(elapsed, 2),
        "prompt": args.prompt
    }
    
    if args.json:
        print(json.dumps(result))
    else:
        print(f"✅ 生成成功: {output_path} ({elapsed:.1f}秒)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
