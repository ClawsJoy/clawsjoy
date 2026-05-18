#!/bin/bash
# 根据 Agent 输出执行对应脚本

USER_INPUT="$1"

case "$USER_INPUT" in
    *拿铁*|*latte*)
        ~/clawsjoy/bin/search_nearby.sh "咖啡店"
        ~/clawsjoy/bin/check_inventory.sh "拿铁"
        ;;
    *美式*|*americano*)
        ~/clawsjoy/bin/search_nearby.sh "咖啡店"
        ~/clawsjoy/bin/check_inventory.sh "美式"
        ;;
    *)
        echo "请问您想要哪种咖啡？拿铁、美式还是卡布奇诺？"
        ;;
esac
