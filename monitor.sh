#!/bin/bash
echo "=== ClawsJoy 监控面板 ==="
echo "时间: $(date)"
echo ""

# 服务状态
echo "📡 服务状态:"
curl -s http://localhost:5002/health | python3 -m json.tool 2>/dev/null || echo "无法获取"

# 进程信息
echo ""
echo "🔄 进程信息:"
ps aux | grep gunicorn | grep -v grep | awk '{print "PID:",$2,"MEM:",$4"%","CPU:",$3"%"}'

# 端口监听
echo ""
echo "🔌 端口监听:"
netstat -tlnp 2>/dev/null | grep 5002

# 磁盘使用
echo ""
echo "💾 磁盘使用:"
df -h /home/flybo/clawsjoy_v5 | tail -1

# 最近日志
echo ""
echo "📝 最后5条错误日志:"
tail -5 logs/error.log 2>/dev/null || echo "无日志文件"
