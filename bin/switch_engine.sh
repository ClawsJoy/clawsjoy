#!/bin/bash
# 切换执行引擎
# 用法: ./switch_engine.sh openclaw|hermes|self

ENGINE=$1
CONFIG_FILE="/mnt/d/clawsjoy/config/engine.json"

if [ -z "$ENGINE" ]; then
    echo "当前引擎: $(cat $CONFIG_FILE 2>/dev/null | grep -o '"executor":"[^"]*"' | cut -d'"' -f4)"
    echo "可用引擎: openclaw, hermes, self"
    exit 0
fi

cat > $CONFIG_FILE << EOF
{
    "executor": "$ENGINE",
    "updated_at": "$(date -Iseconds)"
}
