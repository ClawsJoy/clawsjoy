from lib.smart_config import smart_config
#!/usr/bin/env python3
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
import torch
import time
import os

print("初始化模型...")

# 加载模型
pipe = StableDiffusionXLPipeline.from_pretrained(
    "str(smart_config.ROOT)/models/dreamshaper",
    torch_dtype=torch.float16,
    variant="fp16"
)

# 使用更快的调度器
pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config,
    use_karras_sigmas=True
)

# 内存优化
pipe.enable_model_cpu_offload()
pipe.enable_attention_slicing()

# TF32加速
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

print("✅ 模型就绪")

# 生成测试图片
prompt = "A beautiful sunset over mountains, digital art, 4k, highly detailed"
print(f"🎨 生成中: {prompt}")

start = time.time()
image = pipe(
    prompt=prompt,
    num_inference_steps=15,  # 减少到15步
    height=768,
    width=768,
    guidance_scale=7.0
).images[0]

elapsed = time.time() - start
image.save("optimized_test.png")
print(f"✅ 完成! 耗时: {elapsed:.1f}秒")
print(f"📁 图片已保存: optimized_test.png")
