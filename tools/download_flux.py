import os

import torch
from diffusers import Flux2KleinPipeline

from lib.smart_config import smart_config

print("正在下载 FLUX.2 Klein 4B 模型...")
print("注意：需要约 13GB 显存，首次下载约 8GB")

try:
    pipe = Flux2KleinPipeline.from_pretrained(
        "black-forest-labs/FLUX.2-klein-4B", torch_dtype=torch.bfloat16
    )
    print("✅ FLUX.2 下载完成")
except Exception as e:
    print(f"⚠️ 下载失败: {e}")
    print(
        "可以稍后手动下载: huggingface-cli download black-forest-labs/FLUX.2-klein-4B"
    )
