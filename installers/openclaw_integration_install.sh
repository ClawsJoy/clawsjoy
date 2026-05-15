#!/bin/bash
# ============================================
# ClawsJoy - OpenClaw 集成安装脚本
# 功能：建立软链接，让 OpenClaw 调用 ClawsJoy Skills
# 版本：2.0
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 路径定义
CLAWSJOY_HOME="/home/flybo/clawsjoy"
OPENCLAW_SKILLS="/root/.openclaw/skills"

echo ""
echo -e "${BLUE}=========================================="
echo "  ClawsJoy → OpenClaw 集成安装"
echo "==========================================${NC}"
echo ""

# 步骤1：检查环境
echo -e "${GREEN}[1/6] 检查环境...${NC}"

if [ ! -d "$CLAWSJOY_HOME" ]; then
    echo -e "${RED}❌ ClawsJoy 未安装: $CLAWSJOY_HOME${NC}"
    exit 1
fi
echo -e "${GREEN}  ✅ ClawsJoy 目录存在${NC}"

if ! command -v openclaw >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ OpenClaw 未安装${NC}"
    echo "   请先安装 OpenClaw"
    exit 1
fi
echo -e "${GREEN}  ✅ OpenClaw 已安装${NC}"

# 步骤2：备份现有配置
echo -e "${GREEN}[2/6] 备份现有配置...${NC}"

BACKUP_DIR="${OPENCLAW_SKILLS}/backup_$(date +%Y%m%d_%H%M%S)"
if [ -d "$OPENCLAW_SKILLS" ]; then
    mkdir -p "$BACKUP_DIR"
    cp -r "${OPENCLAW_SKILLS}"/* "${BACKUP_DIR}/" 2>/dev/null || true
    echo -e "${GREEN}  ✅ 已备份到: $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}  ⚠️ 首次安装，跳过备份${NC}"
fi

# 步骤3：创建 Skills 目录
echo -e "${GREEN}[3/6] 创建 Skills 目录...${NC}"
mkdir -p "$OPENCLAW_SKILLS"
echo -e "${GREEN}  ✅ 目录已就绪: $OPENCLAW_SKILLS${NC}"

# 步骤4：创建软链接
echo -e "${GREEN}[4/6] 创建软链接...${NC}"

cd "$OPENCLAW_SKILLS"
find . -maxdepth 1 -type l -exec rm -f {} \; 2>/dev/null
echo "  清理旧链接完成"

LINK_COUNT=0

for skill in auth billing coffee executor memory auto_generated promo queue router spider task tenant; do
    SRC="${CLAWSJOY_HOME}/skills/${skill}"
    if [ -d "$SRC" ]; then
        ln -sf "$SRC" "$skill"
        echo -e "  ${GREEN}✅${NC} $skill"
        LINK_COUNT=$((LINK_COUNT + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC} $skill (目录不存在)"
    fi
done

echo -e "${GREEN}  ✅ 已创建 ${LINK_COUNT} 个软链接${NC}"

# 步骤5：创建兼容包装器
echo -e "${GREEN}[5/6] 创建兼容包装器...${NC}"

cat > promo-wrapper.md << 'EOF'
---
name: clawsjoy-promo
description: 制作城市宣传片
---

# 宣传片制作

## 生成宣传片
```bash
curl -X POST http://localhost:8084/api/task/promo \
  -H "Content-Type: application/json" \
  -d '{"city":"香港","style":"科技","tenant_id":"1"}'
EOF
echo -e " 
G
R
E
E
N
✅
GREEN✅{NC} promo-wrapper.md"

cat > billing-wrapper.md << 'EOF'

name: clawsjoy-billing
description: 查询账户余额
余额查询
bash
curl "http://localhost:8090/api/billing/balance?tenant_id=1"
EOF
echo -e " 
G
R
E
E
N
✅
GREEN✅{NC} billing-wrapper.md"

cat > coffee-wrapper.md << 'EOF'

name: clawsjoy-coffee
description: 咖啡订购

咖啡订购
查看店铺
bash
curl http://localhost:8085/api/coffee/shops
下单
bash
curl -X POST http://localhost:8085/api/coffee/order \
  -H "Content-Type: application/json" \
  -d '{"item":"拿铁","shop_id":1}'
EOF
echo -e " 
G
R
E
E
N
✅
GREEN✅{NC} coffee-wrapper.md"

cat > auth-wrapper.md << 'EOF'

name: clawsjoy-auth
description: 用户认证

认证服务
登录
bash
curl -X POST http://localhost:8092/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
健康检查
bash
curl http://localhost:8092/api/auth/health
EOF
echo -e " 
G
R
E
E
N
✅
GREEN✅{NC} auth-wrapper.md"

步骤6：重启服务
echo -e "
G
R
E
E
N
[
6
/
6
]
重启
O
p
e
n
C
l
a
w
服务
.
.
.
GREEN[6/6]重启OpenClaw服务...{NC}"
systemctl --user restart openclaw-gateway
sleep 10

if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
echo -e "
G
R
E
E
N
✅
O
p
e
n
C
l
a
w
服务已启动
GREEN✅OpenClaw服务已启动{NC}"
else
echo -e "
Y
E
L
L
O
W
⚠
®
服务状态异常，请手动检查
YELLOW⚠ 
R
◯
 服务状态异常，请手动检查{NC}"
fi

完成
echo ""
echo -e "
B
L
U
E
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
"
e
c
h
o
"
✅集成安装完成！
"
e
c
h
o
"
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
=
BLUE=========================================="echo"✅集成安装完成！"echo"=========================================={NC}"
echo ""
echo "📊 安装统计:"
echo " - 软链接数量: ${LINK_COUNT}"
echo " - 包装器数量: 4"
echo ""
echo "🔧 验证命令:"
echo " openclaw agent --agent main -m '查询余额'"
echo " openclaw agent --agent main -m '制作香港宣传片'"
echo ""
echo "🌐 访问地址:"
echo " Joy Mate: http://localhost:8082/joymate/?tenant=1"
echo ""

