#!/usr/bin/env python3
"""DreamShaper 图像生成 - 独立于 SD 1.5"""
import torch, sys, json, time, argparse
from diffusers import StableDiffusionXLPipeline

def load_model():
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "/mnt/d/clawsjoy-open-source/models/dreamshaper",
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    return pipe.to("cuda")

def generate(pipe, prompt, negative="", steps=15, width=768, height=768, cfg=7.5):
    result = pipe(
        prompt=prompt,
        negative_prompt=negative or "low quality, blurry, ugly, deformed",
        num_inference_steps=steps,
        width=width,
        height=height,
        
    )
    return result.images[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--negative", default="")
    parser.add_argument("--steps", type=int, default=15)
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--cfg", type=float, default=7.5)
    parser.add_argument("--output", default="data/vision/dreamshaper_output.png")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    start = time.time()
    pipe = load_model()
    img = generate(pipe, args.prompt, args.negative, args.steps, args.width, args.height, args.cfg)
    img.save(args.output)
    elapsed = time.time() - start

    if args.json:
        print(json.dumps({"success": True, "image_path": args.output, "elapsed_time": elapsed}))
    else:
        print(f"✅ {args.output} ({elapsed:.1f}s)")

def img2img(pipe, image_path, prompt, negative="", steps=15, strength=0.5):
    from PIL import Image
    init = Image.open(image_path).convert("RGB")
    result = pipe(
        prompt=prompt,
        negative_prompt=negative,
        image=init,
        strength=strength,
        num_inference_steps=steps,
    )
    return result.images[0]
