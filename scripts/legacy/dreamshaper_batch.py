from lib.smart_config import smart_config
from diffusers import StableDiffusionXLPipeline
import torch
import time
import os

print("加载 DreamShaper 模型...")
pipe = StableDiffusionXLPipeline.from_pretrained(
    './models/dreamshaper',
    torch_dtype=torch.float16,
    variant='fp16'
)
pipe.enable_model_cpu_offload()
print("✅ 模型就绪\n")

# 提示词列表
prompts = [
    ("日本花园", "A serene Japanese garden with a koi pond, cherry blossoms in full bloom on the trees, soft morning sunlight filtering through the leaves, wooden bridge over the water, highly detailed, photorealistic, 8k"),
    ("夕阳原画", "A breathtaking landscape of a sunset over mountains, with dramatic orange and purple clouds, reflections on a calm lake, cinematic lighting, ultra HD, 8k resolution"),
    ("中国风水墨", "Traditional Chinese ink wash painting, a solitary fisherman on a boat in a misty river, distant mountains fading into the fog, elegant and poetic, minimalist style"),
    ("熊猫吃竹", "A cute panda sitting on a rock, happily eating bamboo, forest background, soft green lighting, vibrant colors, high resolution, sharp focus"),
    ("3D可爱猫", "A cute 3D rendered cartoon of a chubby orange cat, wearing a tiny detective hat, holding a magnifying glass, Pixar style, pastel colors, soft lighting, blind box toy aesthetic, white background"),
    ("赛博猫", "A cute cat with neon glowing cybernetic eyes and sleek dark blue fur, wearing a high-tech collar, standing on a rain-soaked neon-lit street in a futuristic Tokyo cityscape, vibrant magenta and cyan lights, reflections on the wet ground, cinematic lighting, hyper-detailed, 8k, unreal engine 5"),
    ("复古手绘", "A vintage botanical illustration of a red poppy flower, detailed pencil sketch with soft watercolor coloring, aged paper texture, artistic, elegant"),
    ("金毛跳水", "Action shot of a golden retriever dog jumping into a water splash, close-up, sparkling water droplets frozen in mid-air, bright sunlight, joyful expression, high speed photography, 8k"),
    ("咖啡杯", "Product photography of a modern white coffee mug on a wooden table, with coffee beans scattered around, soft warm sunlight from a window, rustic aesthetic, minimalist composition, high resolution"),
    ("科幻摩托", "Concept art of a futuristic cyberpunk motorcycle with neon blue lights, parked in a rainy alley, dark moody atmosphere, highly detailed, 8k, unreal engine 5"),
]

os.makedirs("dreamshaper_outputs", exist_ok=True)

for i, (name, prompt) in enumerate(prompts, 1):
    print(f"[{i}/{len(prompts)}] 生成: {name}")
    start = time.time()
    
    image = pipe(
        prompt=prompt,
        num_inference_steps=15,
        height=768,
        width=768,
        guidance_scale=7.5
    ).images[0]
    
    elapsed = time.time() - start
    filename = f"dreamshaper_outputs/{name}.png"
    image.save(filename)
    print(f"  ✅ 完成: {filename} ({elapsed:.1f}秒)\n")

print(f"🎉 全部完成！共 {len(prompts)} 张图片保存在 dreamshaper_outputs/")
