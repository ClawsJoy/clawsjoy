#!/bin/bash
# 自动启动 ComfyUI 后台服务

cd /mnt/d/clawsjoy_clean/tools/ComfyUI

# 确保日志目录存在
mkdir -p /mnt/d/clawsjoy_clean/logs

# 检查是否已运行
if curl -s http://127.0.0.1:8188/system_stats > /dev/null 2>&1; then
    echo "ComfyUI 已在运行"
    exit 0
fi

# 启动服务
nohup python main.py --listen 0.0.0.0 --port 8188 > /mnt/d/clawsjoy_clean/logs/comfyui.log 2>&1 &
echo "ComfyUI 已启动，PID: $!"
sleep 8

# 等待就绪
for i in {1..15}; do
    if curl -s http://127.0.0.1:8188/system_stats > /dev/null 2>&1; then
        echo "ComfyUI 就绪"
        break
    fi
    echo "等待 ComfyUI 启动... ($i/15)"
    sleep 2
done
