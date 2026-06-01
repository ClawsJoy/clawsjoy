from lib.smart_config import smart_config
"""下载 FLUX.1-schnell 模型"""
import os
from diffusers import FluxPipeline
import torch

print("正在下载 FLUX.1-schnell 模型...")
print("模型大小: ~7GB")
print("显存需求: 6-8GB")
print("预计时间: 10-30分钟（取决于网速）")
print("")

try:
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-schnell",
        torch_dtype=torch.bfloat16
    )
    print("\n✅ FLUX.1-schnell 下载完成！")
    
    # 测试生成
    print("\n测试生成图像...")
    image = pipe(
        "a cute cat, cartoon style",
        guidance_scale=0.0,
        num_inference_steps=4,
        max_sequence_length=256,
        height=512,
        width=512
    ).images[0]
    
    image.save("output/flux_test.png")
    print("✅ 测试图像已生成: output/flux_test.png")
    
except Exception as e:
    print(f"❌ 下载失败: {e}")
    print("")
    print("备选方案：使用 huggingface-cli")
    print("huggingface-cli download black-forest-labs/FLUX.1-schnell")
