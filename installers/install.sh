#!/bin/bash
echo "🔗 配置 ClawsJoy → OpenClaw 软链接..."

mkdir -p /root/.openclaw/skills
cd /root/.openclaw/skills

for skill in auth billing coffee executor memory auto_generated promo queue router spider task tenant; do
    if [ -d "/home/flybo/clawsjoy/skills/$skill" ]; then
        ln -sf "/home/flybo/clawsjoy/skills/$skill" "$skill"
        echo "  ✅ $skill"
    fi
done

systemctl --user restart openclaw-gateway
echo "✅ 安装完成"
