#!/bin/bash
echo "🔧 工程师 Agent 检查"

# 检查服务
for svc in agent-api chat-api promo-api; do
    if pm2 list | grep -q "$svc.*online"; then
        echo "✅ $svc"
    else
        echo "❌ $svc"
        pm2 start $svc 2>/dev/null || cd bin && pm2 start ${svc}.py --name $svc
    fi
done

echo ""
echo "📊 服务状态:"
pm2 list | grep -E "online|errored"
