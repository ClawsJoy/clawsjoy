from lib.smart_config import smart_config
#!/usr/bin/env python3
from diffusers import StableDiffusionXLPipeline
import torch
import time

# 模型路径
model_path = "str(smart_config.ROOT)/models/dreamshaper"

print("正在加载 DreamShaper XL...")
print(f"显存: {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB")

# 加载模型（fp16 + CPU offload 优化）
pipe = StableDiffusionXLPipeline.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
)

# 6GB 显存优化
pipe.enable_model_cpu_offload()  # 自动将部分模型移到 CPU
pipe.enable_attention_slicing()   # 降低显存占用

print("✅ 模型加载成功！")

# 生成测试图片
prompt = "A beautiful sunset over mountains, digital art, 4k, highly detailed"
print(f"\n🎨 生成中: {prompt}")

start = time.time()
image = pipe(
    prompt=prompt,
    num_inference_steps=25,
    height=768,
    width=768,
    guidance_scale=7.5
).images[0]

elapsed = time.time() - start
print(f"✅ 生成完成！耗时: {elapsed:.1f}秒")

# 保存图片
output_path = "test_dreamshaper.png"
image.save(output_path)
print(f"📁 图片已保存: {output_path}")
