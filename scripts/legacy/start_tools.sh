#!/bin/bash
echo "启动 ClawsJoy 工具集"

# 启动 ComfyUI（后台）
cd /mnt/d/clawsjoy_clean/tools/ComfyUI
nohup python main.py --listen 0.0.0.0 --port 8188 > /tmp/comfyui.log 2>&1 &
echo "✅ ComfyUI 启动: http://localhost:8188"

# 启动 KubeezCut（如果 Node.js 已安装）
if command -v npm &> /dev/null; then
    cd /mnt/d/clawsjoy_clean/tools/KubeezCut
    nohup npm run dev > /tmp/kubeezcut.log 2>&1 &
    echo "✅ KubeezCut 启动: http://localhost:5173"
fi

echo ""
echo "工具已启动，访问地址："
echo "  ComfyUI: http://localhost:8188"
echo "  KubeezCut: http://localhost:5173"
