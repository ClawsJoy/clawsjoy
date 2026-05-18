#!/bin/bash
cd /mnt/d/clawsjoy

case "$1" in
    dashboard)
        python3 intelligence/dashboard.py
        ;;
    logs)
        python3 intelligence/log_analyzer.py
        ;;
    perf)
        python3 intelligence/performance_monitor.py
        ;;
    recommend)
        python3 intelligence/recommendation_engine.py
        ;;
    all)
        echo "📊 运行所有智能分析..."
        python3 intelligence/dashboard.py
        ;;
    status)
        ./show_status.sh
        ;;
    *)
        echo "用法: $0 {dashboard|logs|perf|recommend|all|status}"
        echo ""
        echo "命令说明:"
        echo "  dashboard  - 显示智能仪表盘"
        echo "  logs       - 分析日志"
        echo "  perf       - 性能监控"
        echo "  recommend  - 智能推荐"
        echo "  all        - 运行全部"
        echo "  status     - 服务状态"
        ;;
esac
