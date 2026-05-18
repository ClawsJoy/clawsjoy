#!/bin/bash
cd /mnt/d/clawsjoy

if pgrep -f agent_gateway_web > /dev/null; then
    echo "✅ ClawsJoy 运行中"
    curl -s http://localhost:5002/api/health | python3 -m json.tool 2>/dev/null
else
    echo "❌ ClawsJoy 未运行"
    echo "启动: ./start_clawsjoy.sh"
fi
