#!/bin/bash
# ClawsJoy v5 停止脚本

echo "🛑 停止 ClawsJoy v5..."

pkill -f "agent_gateway_enhanced"
pkill -f "llm_service_optimized"
# 不停止 Ollama，可能被其他服务使用

echo "✅ 服务已停止"
