#!/bin/bash
# 资源监控

MEM=$(ps aux | grep agent_gateway_web | grep -v grep | awk '{print $4}')
CPU=$(ps aux | grep agent_gateway_web | grep -v grep | awk '{print $3}')
DISK=$(df -h / | tail -1 | awk '{print $5}')

echo "{\"timestamp\":\"$(date -Iseconds)\",\"memory\":\"$MEM\",\"cpu\":\"$CPU\",\"disk\":\"$DISK\"}" >> /mnt/d/clawsjoy/logs/metrics.log

# 告警
if [ "${DISK%\%}" -gt 80 ]; then
    echo "⚠️ 磁盘使用率 $DISK" >> /mnt/d/clawsjoy/logs/alerts.log
fi

# D 盘空间预警（D 盘是 /mnt/d）
D_DISK=$(df -h /mnt/d | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$D_DISK" -gt 85 ]; then
    echo "⚠️ D 盘使用率 ${D_DISK}%，请及时清理" | tee -a logs/alerts.log
fi
