#!/bin/bash
cd /mnt/d/clawsjoy

echo "🤖 ClawsJoy 自动修复系统"
echo "========================"
echo ""

# 1. 检查并修复服务
echo "📡 检查服务状态..."
for port in 5002 5003 5005 5008; do
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "  ✅ :$port"
    else
        echo "  ❌ :$port - 尝试修复..."
        ./restart_services.sh 2>/dev/null
        sleep 3
        if curl -s http://localhost:$port/health >/dev/null 2>&1; then
            echo "  ✅ :$port 修复成功"
        else
            echo "  ❌ :$port 修复失败"
        fi
    fi
done

# 2. 检查端口冲突并清理
echo ""
echo "🔌 检查端口冲突..."
for port in 5002 5003 5005 5008; do
    PID=$(lsof -t -i:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "  端口 $port 被 PID:$PID 占用"
    fi
done

# 3. 清理僵尸进程
echo ""
echo "🧹 清理僵尸进程..."
pkill -f "defunct" 2>/dev/null
echo "  完成"

# 4. 检查磁盘空间
echo ""
echo "💾 检查磁盘空间..."
usage=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $usage -gt 85 ]; then
    echo "  ⚠️ 磁盘使用率: ${usage}%"
    echo "  清理旧日志..."
    find logs -name "*.log" -mtime +7 -delete 2>/dev/null
else
    echo "  ✅ 磁盘正常: ${usage}%"
fi

# 5. 显示修复结果
echo ""
echo "========================"
echo "✅ 自动修复完成"

# 显示最终状态
./status_simple.sh 2>/dev/null
