#!/bin/bash
# ClawsJoy 自我升级监控系统启动脚本

echo "🚀 启动 ClawsJoy 自我升级监控系统"
echo "=================================="

# 1. 启动网关（如果未运行）
if ! pgrep -f "agent_gateway_enhanced.py" > /dev/null; then
    echo "📡 启动 API 网关..."
    python3 agent_gateway_enhanced.py &
    sleep 3
fi

# 2. 启动 Streamlit 面板
echo "📊 启动 Web 监控面板..."
streamlit run web/upgrade_dashboard.py --server.port 8501 --server.address 0.0.0.0 &

# 3. 启动自动升级守护进程（可选）
echo "🤖 启动自动升级守护进程..."
nohup python3 auto_upgrade_complete.py --continuous > logs/auto_upgrade.log 2>&1 &

echo ""
echo "✅ 系统已启动！"
echo "🌐 Web 面板: http://localhost:8501"
echo "📡 API 端点: http://localhost:5000/api/v5"
echo "📝 日志目录: logs/"
echo ""
echo "查看实时日志: tail -f logs/auto_upgrade.log"
