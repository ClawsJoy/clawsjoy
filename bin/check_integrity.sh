#!/bin/bash
# 数据完整性校验

CD /mnt/d/clawsjoy
FAILED=0

# 校验用户数据
for f in data/users/*.json; do
    if [ -f "$f" ]; then
        if ! python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
            echo "❌ 损坏: $f"
            FAILED=$((FAILED+1))
        fi
    fi
done

# 校验大脑数据
if [ -f data/brain_v2.json ]; then
    if ! python3 -c "import json; json.load(open('data/brain_v2.json'))" 2>/dev/null; then
        echo "❌ 损坏: data/brain_v2.json"
        FAILED=$((FAILED+1))
    fi
fi

if [ $FAILED -eq 0 ]; then
    echo "✅ 所有数据完整"
else
    echo "⚠️ 发现 $FAILED 个损坏文件"
fi
