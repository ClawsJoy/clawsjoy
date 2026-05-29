#!/bin/bash
# 完整的咖啡订购工作流（模拟共生架构）

TENANT_ID=${1:-1}
COFFEE_TYPE=${2:-拿铁}

echo "=========================================="
echo "☕ 租户 ${TENANT_ID} 咖啡订购流程"
echo "用户: 我想喝${COFFEE_TYPE}"
echo "=========================================="

# 阶段1: 搜索附近咖啡店（ClawsJoy 执行）
echo ""
echo "📡 [ClawsJoy] 搜索附近咖啡店..."
STORES=$(~/clawsjoy/bin/search_nearby.sh "咖啡店")
echo "$STORES"

# 阶段2: 检查库存（ClawsJoy 执行）
echo ""
echo "📦 [ClawsJoy] 检查 ${COFFEE_TYPE} 库存..."
INVENTORY=$(~/clawsjoy/bin/check_inventory.sh "$COFFEE_TYPE")
echo "$INVENTORY"

# 阶段3: 选择最佳门店（简单逻辑）
echo ""
echo "🤔 [OpenClaw] 分析推荐..."
BEST_STORE="星巴克"

# 阶段4: 下单（ClawsJoy 执行）
echo ""
echo "🛒 [ClawsJoy] 下单 $COFFEE_TYPE..."
RESULT=$(~/clawsjoy/bin/place_order.sh "$COFFEE_TYPE" "$BEST_STORE" "$TENANT_ID")
echo "$RESULT"

echo ""
echo "=========================================="
echo "✅ 咖啡订购完成"
echo "=========================================="
