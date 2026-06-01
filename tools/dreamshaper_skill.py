from lib.smart_config import smart_config
#!/usr/bin/env python3
import sys
import json
import argparse
import time
import os
from diffusers import StableDiffusionXLPipeline
import torch

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--negative_prompt', default='low quality, blurry, ugly')
    parser.add_argument('--steps', type=int, default=15)
    parser.add_argument('--width', type=int, default=768)
    parser.add_argument('--height', type=int, default=768)
    parser.add_argument('--cfg', type=float, default=7.5)
    parser.add_argument('--json', action='store_true')
    
    args = parser.parse_args()
    
    pipe = StableDiffusionXLPipeline.from_pretrained(
        'str(smart_config.ROOT)/models/dreamshaper',
        torch_dtype=torch.float16,
        variant='fp16'
    )
    pipe.enable_model_cpu_offload()
    
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
    output_path = f"output/dreamshaper_{int(time.time())}.png"
    os.makedirs('output', exist_ok=True)
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
