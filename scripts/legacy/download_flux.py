from lib.smart_config import smart_config
import os
from huggingface_hub import snapshot_download
import time

# 设置镜像站（国内加速）
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 如果需要 token，在这里设置（如果你之前已经在环境变量里设置过，可以省略）
# os.environ['HF_TOKEN'] = 'hf_xxxxxx'

print("=" * 50)
print("开始下载 FLUX.1-schnell 模型")
print("=" * 50)
print("模型大小: ~7GB")
print("预计时间: 取决于网速，可能 10-30 分钟")
print("")

# 重试机制
max_retries = 3
for attempt in range(max_retries):
    try:
        print(f"尝试 {attempt + 1}/{max_retries}...")
        
        snapshot_download(
            repo_id="black-forest-labs/FLUX.1-schnell",
            local_dir="./models/FLUX.1-schnell",
            local_dir_use_symlinks=False,
            resume_download=True,
            max_workers=4,  # 降低并发数，更稳定
        )
        
        print("\n✅ 下载完成！")
        
        # 验证文件
        model_dir = "./models/FLUX.1-schnell"
        if os.path.exists(f"{model_dir}/model_index.json"):
            print("✅ 模型文件验证成功")
        else:
            print("⚠️ 模型文件可能不完整，请检查")
        break
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        if attempt < max_retries - 1:
            print(f"等待 10 秒后重试...")
            time.sleep(10)
        else:
            print("\n请检查网络连接，或尝试使用其他方法")
            print("\n备选方案：使用 hfd 工具下载")
            print("  wget https://hf-mirror.com/hfd/hfd.sh")
            print("  chmod a+x hfd.sh")
            print("  ./hfd.sh black-forest-labs/FLUX.1-schnell --local-dir ./models/FLUX.1-schnell")
