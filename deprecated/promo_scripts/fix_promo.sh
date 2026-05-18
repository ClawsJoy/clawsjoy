#!/bin/bash
# 修复 Promo API 的核心问题

cd /mnt/d/clawsjoy/bin

# 备份原文件
cp promo_api.py promo_api.py.bak

# 确保 Unsplash 采集有超时和重试
sed -i 's/timeout=15/timeout=30/g' promo_api.py
sed -i 's/requests.get/requests.get/g' promo_api.py

# 添加本地图片降级
grep -q "本地图片" promo_api.py || sed -i '/def fetch_images/a\    # 本地图片降级\n    if not images:\n        local_dir = Path("/mnt/d/clawsjoy/web/images/local")\n        if local_dir.exists():\n            local_images = list(local_dir.glob("*.jpg"))\n            images = [str(img) for img in local_images[:count]]\n            print(f"使用本地图片: {len(images)}张")' promo_api.py

pm2 restart promo-api
echo "✅ Promo API 已修复"
