#!/bin/bash
# 每日采集工作流（不生成视频）

cd /mnt/d/clawsjoy

echo "=== 采集工作流 ==="
echo "开始时间: $(date)"

# 1. 采集香港新闻/政策资料
echo "[1/4] 采集资料库..."
python3 spiders/hk_spider.py 2>&1 | tee -a logs/collect.log

# 2. 采集图片（关键词）
echo "[2/4] 采集图片..."
python3 -c "
from bin.promo_api import fetch_images
keywords = ['Hong Kong government', 'Hong Kong university', 'Hong Kong street', 'Hong Kong harbour']
for kw in keywords:
    images = fetch_images(kw, 8)
    print(f'{kw}: {len(images)} 张')
" 2>&1 | tee -a logs/collect.log

# 3. 生成话题列表
echo "[3/4] 生成话题..."
python3 skills/topic_planner/execute.py '{"category": "all"}' > output/topics/today.json

# 4. 统计
echo "[4/4] 统计..."
echo "图片数: $(ls web/images/*.jpg 2>/dev/null | wc -l)"
echo "资料数: $(find tenants/tenant_1/library -name '*.txt' 2>/dev/null | wc -l)"

echo "完成时间: $(date)"
