#!/bin/bash
# 一键加载 OpenClaw 环境配置

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../config"

# 加载环境变量
source "$CONFIG_DIR/openclaw_env.sh"

# 配置软链接
source "$CONFIG_DIR/openclaw_links.sh"
setup_links

# 重启 OpenClaw 使配置生效
echo "重启 OpenClaw..."
systemctl --user restart openclaw-gateway
sleep 10

echo ""
echo "=========================================="
echo "✅ ClawsJoy OpenClaw 环境已就绪"
echo "=========================================="
echo ""
echo "测试命令:"
echo "  openclaw agent --agent main -m '查询余额'"
echo "  openclaw agent --agent main -m '制作香港宣传片'"
echo ""
echo "环境变量:"
echo "  CLAWSJOY_TASK_API=$CLAWSJOY_TASK_API"
echo "  CLAWSJOY_SKILLS=$CLAWSJOY_SKILLS"
echo ""

