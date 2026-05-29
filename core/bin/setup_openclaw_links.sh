#!/bin/bash
# ClawsJoy → OpenClaw 软链接一键配置脚本

set -e

echo "=========================================="
echo "🔗 ClawsJoy → OpenClaw 软链接配置"
echo "=========================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

CLAWSJOY_SKILLS="/home/flybo/clawsjoy/skills"
OPENCLAW_SKILLS="/root/.openclaw/skills"

# 检查源目录
if [ ! -d "$CLAWSJOY_SKILLS" ]; then
    echo -e "${RED}❌ ClawsJoy Skills 目录不存在: $CLAWSJOY_SKILLS${NC}"
    exit 1
fi

# 创建目标目录
mkdir -p "$OPENCLAW_SKILLS"
echo -e "${GREEN}✅ OpenClaw skills 目录已就绪${NC}"

cd "$OPENCLAW_SKILLS"

# 备份旧配置
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
if [ -d "backup_*" ] 2>/dev/null; then
    echo "跳过备份（已有备份）"
else
    mkdir -p "$BACKUP_DIR"
    cp -r . "$BACKUP_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✅ 已备份到 $BACKUP_DIR${NC}"
fi

# 删除旧链接
echo "清理旧链接..."
find . -maxdepth 1 -type l -exec rm -f {} \;

echo ""
echo "创建软链接..."

# Skills 列表
SKILLS_LIST="auth billing coffee executor memory auto_generated promo queue router spider task tenant"

for skill in $SKILLS_LIST; do
    SRC="$CLAWSJOY_SKILLS/$skill"
    if [ -d "$SRC" ]; then
        rm -f "$skill"
        ln -sf "$SRC" "$skill"
        echo -e "  ${GREEN}✅${NC} $skill → $SRC"
    else
        echo -e "  ${YELLOW}⚠️${NC} $skill 不存在，跳过"
    fi
done

# 验证结果
echo ""
echo "=========================================="
echo "🔍 验证结果"
echo "=========================================="
LINK_COUNT=$(find . -maxdepth 1 -type l | wc -l)
echo -e "${GREEN}✅ 已创建 $LINK_COUNT 个软链接${NC}"

echo ""
echo "软链接列表:"
ls -la | grep " -> " | awk '{print $9, "→", $11}'

echo ""
echo "=========================================="
echo "✅ 软链接配置完成"
echo "=========================================="
echo ""
echo "下一步："
echo "  systemctl --user restart openclaw-gateway"
echo "  openclaw agent --agent main -m '查询余额'"
echo ""

