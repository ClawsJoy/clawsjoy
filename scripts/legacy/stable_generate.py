from lib.smart_config import smart_config
from diffusers import StableDiffusionXLPipeline
import torch
import time

print("加载模型...")
pipe = StableDiffusionXLPipeline.from_pretrained(
    "str(smart_config.ROOT)/models/dreamshaper",
    torch_dtype=torch.float16,
    variant="fp16"
)
pipe.enable_model_cpu_offload()
pipe.enable_attention_slicing()
print("✅ 模型就绪\n")

# 测试不同参数
prompt = "A beautiful sunset over mountains, digital art"

configs = [
    (8, 512, "快速"),
    (12, 640, "平衡"),
    (15, 768, "高质量"),
]

for steps, size, name in configs:
    print(f"{name}模式 ({steps}步, {size}x{size}):")
    start = time.time()
    image = pipe(
        prompt=prompt,
        num_inference_steps=steps,
        height=size,
        width=size,
        guidance_scale=7.0
    ).images[0]
    elapsed = time.time() - start
    image.save(f"{name}_{steps}steps.png")
    print(f"  耗时: {elapsed:.1f}秒\n")

print("✅ 测试完成！")
