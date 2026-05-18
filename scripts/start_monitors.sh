#!/bin/bash
cd /mnt/d/clawsjoy_clean

# 启动性能监控（循环运行）
nohup bash -c 'while true; do python3 intelligence/performance_monitor.py; sleep 60; done' > logs/performance_monitor.log 2>&1 &
echo "✅ performance_monitor 已启动"

# 启动成功率监控（循环运行）
nohup bash -c 'while true; do python3 intelligence/success_monitor.py; sleep 300; done' > logs/success_monitor.log 2>&1 &
echo "✅ success_monitor 已启动"

# 启动告警器（循环运行）
nohup bash -c 'while true; do python3 intelligence/alerter.py; sleep 60; done' > logs/alerter.log 2>&1 &
echo "✅ alerter 已启动"

echo "所有监控已启动"
