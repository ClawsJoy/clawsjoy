#!/bin/bash
# ClawsJoy 网关启动脚本

cd /home/flybo/clawsjoy_v5
nohup python3 agent_gateway_enhanced.py > gateway.log 2>&1 &
echo "Gateway started at $(date)" >> gateway.log
