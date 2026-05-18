#!/bin/bash
MISSING=0
for f in agent_core/brain_connector.py agent_core/simple_vector.py bin/auto_heal.sh; do
    if [ ! -f "/mnt/d/clawsjoy/$f" ]; then
        echo "❌ 缺失: $f"
        MISSING=1
    fi
done
if [ $MISSING -eq 0 ]; then
    echo "✅ 所有核心文件完整"
fi
