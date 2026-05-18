#!/bin/bash
echo "停止 ClawsJoy 服务..."
pkill -f "agent_gateway_web"
pkill -f "file_service_complete"
pkill -f "multi_agent_service"
pkill -f "doc_generator"
echo "服务已停止"
