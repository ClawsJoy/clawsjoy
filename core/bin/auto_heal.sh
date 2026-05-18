#!/bin/bash
cd /mnt/d/clawsjoy

for service in agent-api chat-api promo-api health-api gateway web; do
    if ! pm2 show $service 2>/dev/null | grep -q "status.*online"; then
        echo "[$(date)] ⚠️ $service 异常，重启..."
        pm2 restart $service
        sleep 1
    fi
done
pm2 save
