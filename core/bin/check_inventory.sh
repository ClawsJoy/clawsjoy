#!/bin/bash
# check_inventory.sh - 检查指定咖啡库存
ITEM=$1
echo "{\"status\":\"success\",\"item\":\"$ITEM\",\"available_stores\":[\"星巴克\",\"瑞幸\"]}"
