#!/bin/bash
# 2026年批量内容生产

echo "=== 2026年香港内容批量生产 ==="
echo "开始时间: $(date)"
echo ""

cat topics_2026.txt | while read topic; do
    echo "📌 处理: $topic"
    
    # 生成脚本
    python3 cmd/writer_2026.py "$topic" > "output/scripts/2026_${topic:0:30}.txt"
    echo "   ✅ 脚本已生成"
    
    # 制作视频
    curl -s -X POST http://localhost:8105/api/promo/make \
        -H "Content-Type: application/json" \
        -d '{"city":"香港","style":"人文"}' > /dev/null
    echo "   ✅ 视频已生成"
    
    echo ""
    sleep 2
done

echo "完成时间: $(date)"
