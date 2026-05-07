#!/bin/bash
echo "=== ClawsJoy 健康检查 ==="
echo ""
echo "📡 服务状态:"
pm2 list | grep -E "online|errored"

echo ""
echo "🔌 端口监听:"
for port in 18109 8108 18103 18083 16380 19001; do
    if ss -tlnp | grep -q ":$port "; then
        echo "✅ $port 已监听"
    else
        echo "❌ $port 未监听"
    fi
done

echo ""
echo "🎬 最新视频:"
ls -lt /mnt/d/clawsjoy/web/videos/ | head -4

echo ""
echo "📊 磁盘使用:"
df -h /mnt/d | tail -1

echo ""
echo "✅ 检查完成"
