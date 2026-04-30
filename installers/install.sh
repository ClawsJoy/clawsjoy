#!/bin/bash
# ClawsJoy - OpenClaw 软链接配置脚本
# 用法: ./install.sh [CLAWSJOY_PATH] [OPENCLAW_SKILLS_PATH]

CLAWSJOY_HOME="${1:-/opt/clawsjoy}"
OPENCLAW_SKILLS="${2:-$HOME/.openclaw/skills}"

echo "🔗 配置 ClawsJoy → OpenClaw 软链接..."
echo "  ClawsJoy 路径: $CLAWSJOY_HOME"
echo "  OpenClaw Skills: $OPENCLAW_SKILLS"

mkdir -p "$OPENCLAW_SKILLS"
cd "$OPENCLAW_SKILLS"

for skill in auth billing coffee executor memory auto_generated promo queue router spider task tenant; do
    SRC="$CLAWSJOY_HOME/skills/$skill"
    if [ -d "$SRC" ]; then
        ln -sf "$SRC" "$skill"
        echo "  ✅ $skill"
    else
        echo "  ⚠️ $skill 不存在"
    fi
done

echo "✅ 配置完成"
