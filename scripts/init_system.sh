#!/bin/bash
# ClawsJoy 系统初始化脚本

cd /mnt/d/clawsjoy

echo "🔧 初始化 ClawsJoy 智能系统..."

# 创建必要目录
mkdir -p logs output/data/bg output/characters data/hot_db

# 加载定时任务
crontab config/crontab_config.txt
echo "✅ 定时任务已加载"

# 启动智能监控
nohup python3 intelligence/monitor.py > logs/monitor.log 2>&1 &
nohup python3 intelligence/analyzer_daemon.py > logs/analyzer_daemon.log 2>&1 &
nohup python3 intelligence/scheduler.py > logs/scheduler.log 2>&1 &
nohup python3 intelligence/decision_engine_v2.py > logs/decision_engine.log 2>&1 &
nohup python3 agents/true_intelligence_light.py > logs/smart_core.log 2>&1 &

echo "✅ 智能进程已启动"

# 等待服务启动
sleep 3

# 健康检查
./scripts/health_check.sh

echo "✅ 系统初始化完成"
