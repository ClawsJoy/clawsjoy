#!/bin/bash
# ClawsJoy OpenClaw 环境配置模板
# 复制此文件为 openclaw_env.sh 并修改路径

export CLAWSJOY_HOME="/opt/clawsjoy"
export OPENCLAW_SKILLS="$HOME/.openclaw/skills"

# API 端点（可修改）
export CLAWSJOY_TASK_API="http://localhost:8084"
export CLAWSJOY_AUTH_API="http://localhost:8092"
export CLAWSJOY_TENANT_API="http://localhost:8088"
export CLAWSJOY_BILLING_API="http://localhost:8090"
export CLAWSJOY_COFFEE_API="http://localhost:8085"

echo "✅ ClawsJoy 环境已加载"
