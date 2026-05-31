#!/bin/bash
# 定时任务管理脚本

case "$1" in
    disable)
        echo "禁用旧定时任务..."
        crontab -l | grep -v "learning_loop\|auto_evolve\|collector_scheduler\|cleanup_hot_topics" | crontab -
        echo "✅ 已禁用，由事件驱动替代"
        ;;
    enable)
        echo "恢复定时任务..."
        # 恢复逻辑
        ;;
    status)
        echo "当前定时任务:"
        crontab -l | grep -v "^#"
        ;;
    *)
        echo "用法: $0 {disable|enable|status}"
        ;;
esac
