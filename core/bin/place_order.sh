#!/bin/bash
# place_order.sh - 下单
ITEM=$1
STORE=$2
TENANT_ID=${3:-1}
echo "{\"status\":\"success\",\"message\":\"已为您在 ${STORE} 下单 ${ITEM}，预计15分钟送达\",\"order_id\":\"ORD_$(date +%Y%m%d%H%M%S)\"}"
# 记录订单到租户目录
echo "$(date): 租户${TENANT_ID} 在 ${STORE} 下单 ${ITEM}" >> ~/clawsjoy/tenants/tenant_${TENANT_ID}/orders.log
