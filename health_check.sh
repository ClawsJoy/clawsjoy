#!/bin/bash
echo "=== ClawsJoy 监控 ==="
echo "时间: $(date)"

# 1. 服务状态
if curl -s http://localhost:5002/health > /dev/null; then
    echo "✅ 服务运行中 (端口 5002)"
else
    echo "❌ 服务无响应"
fi

# 2. 进程状态
WORKERS=$(ps aux | grep gunicorn | grep -v grep | wc -l)
echo "📊 Gunicorn workers: $WORKERS"

# 3. 磁盘使用
DISK=$(df -h / | awk 'NR==2 {print $5}')
echo "💾 磁盘使用: $DISK"

# 4. 内存使用
MEM=$(ps aux | grep python | awk '{sum+=$6} END {print sum/1024 " MB"}')
echo "🧠 Python 内存: $MEM"

# 5. 数据库文件大小
echo "🗄️ 数据库文件:"
find data/ -name "*.db" -size +10M -exec ls -lh {} \;
