#!/bin/bash

echo "========================================="
echo "   ClawsJoy/JoyMate 服务状态"
echo "========================================="

# 检查 Web
if pgrep -f "http.server 8082" > /dev/null; then
    echo "✅ Web 服务器 (8082) - 运行中"
else
    echo "❌ Web 服务器 (8082) - 未运行"
fi

# 检查 Chat API
if pgrep -f "chat_api_agent" > /dev/null; then
    echo "✅ Chat API (8101) - 运行中"
else
    echo "❌ Chat API (8101) - 未运行"
fi

# 检查 TTS
if pgrep -f "tts_server_stable" > /dev/null; then
    echo "✅ TTS 服务 (9000) - 运行中"
else
    echo "❌ TTS 服务 (9000) - 未运行"
fi

# 检查 JoyMate API
if pgrep -f "joymate_api" > /dev/null; then
    echo "✅ JoyMate API (8093) - 运行中"
else
    echo "❌ JoyMate API (8093) - 未运行"
fi

echo ""
echo "端口监听:"
netstat -tlnp 2>/dev/null | grep -E "8082|8093|8101|9000" | awk '{print "  " $4}'

echo ""
echo "进程 PID:"
ps aux | grep -E "http.server|chat_api|tts_server|joymate_api" | grep -v grep | awk '{print "  " $2 ": " $11 " " $12 " " $13}'
