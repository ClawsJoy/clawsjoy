import os

from lib.smart_config import smart_config

print("正在下载 HiDream-O1-Image 模型...")
print("注意：需要约 16GB 显存")

try:
    from diffusers import DiffusionPipeline

    pipe = DiffusionPipeline.from_pretrained(
        "HiDream-ai/HiDream-O1-Image", torch_dtype=torch.float16
    )
    print("✅ HiDream-O1-Image 下载完成")
except Exception as e:
    print(f"⚠️ 下载失败: {e}")
