#!/bin/bash
# ClawsJoy 4.0 状态查看脚本

echo "=========================================="
echo "ClawsJoy 4.0 系统状态"
echo "=========================================="
echo ""

# 1. 进程状态
echo "1. 进程状态:"
ps aux | grep -E "auth_service|driver_service|user_preference|web_dashboard_secure|agent_watchdog" | grep -v grep | awk '{print "  ✅ " $NF}'
echo ""

# 2. 端口状态
echo "2. 端口状态:"
for port in 5443 5444 5445 5446 5002 5011 11434 8188; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo "  ✅ 端口 $port 已监听"
    else
        echo "  ❌ 端口 $port 未监听"
    fi
done
echo ""

# 3. Agent 状态
echo "3. Agent 状态:"
python3 -c "
from lib.agent_registry import agent_registry
stats = agent_registry.get_stats()
print(f'  总 Agent: {stats[\"total\"]}, 活跃: {stats[\"active\"]}')
for a in stats.get('agents', []):
    print(f'    - {a}')
" 2>/dev/null || echo "   Agent 注册中心未响应"
echo ""

# 4. 健康检查
echo "4. 健康检查:"
# 直接调用 Python 进行健康检查
python3 << 'PYEOF'
import requests
import urllib3
urllib3.disable_warnings()

services = [
    ("auth_service", 5444, "/health"),
    ("driver_service", 5443, "/health"),
    ("preference_service", 5445, "/health"),
    ("web_dashboard", 5446, "/api/health"),
    ("ollama", 11434, "/api/tags"),
]

for name, port, path in services:
    url = f"https://localhost:{port}{path}"
    if port == 11434:
        url = f"http://localhost:{port}{path}"
    try:
        resp = requests.get(url, timeout=3, verify=False)
        if resp.status_code == 200:
            print(f"   ✅ {name}: up")
        else:
            print(f"   ⚠️ {name}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"   ❌ {name}: down")
PYEOF

echo ""
echo "=========================================="
