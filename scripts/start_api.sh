#!/bin/bash
cd /home/flybo/clawsjoy_clean

# 清理端口
echo "清理端口 8000..."
pkill -f "python3.*api"
sleep 2

# 确保端口释放
if lsof -i :8000 > /dev/null 2>&1; then
    echo "强制释放端口..."
    kill -9 $(lsof -t -i:8000) 2>/dev/null
    sleep 1
fi

# 启动服务（使用修复版）
echo "启动 FastAPI 服务..."
export PYTHONPATH=/home/flybo/clawsjoy_clean
python3 api_fast_fixed.py

# 或者如果是 api_final.py，需要先修复
# python3 api_final.py
