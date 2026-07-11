#!/bin/bash
echo "🛑 停止 ClawsJoy 服务..."

pkill -f "agent_gateway_enhanced"
pkill -f "streamlit"
pkill -f "discord_bot_poll"
pkill -f "webui.py"

echo "✅ 已停止"
