#!/bin/bash
echo "🦞 Agent 工程师日报"
echo "=================="
echo ""

echo "📊 服务状态:"
pm2 list | grep -E "online|errored"

echo ""
echo "📈 关键词统计:"
curl -s -X POST http://localhost:18109/api/agent -d '{"text":"关键词统计"}' -H "Content-Type: application/json" | jq '.message'

echo ""
echo "💾 磁盘使用:"
df -h /mnt/d | tail -1

echo ""
echo "📁 备份文件:"
ls -lt /mnt/d/backups/clawsjoy/*.tar.gz 2>/dev/null | head -3 | awk '{print $9, $5}'

echo ""
echo "✅ 日报完成"
