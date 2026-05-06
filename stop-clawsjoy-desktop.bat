@echo off
title ClawsJoy 停止器
color 0C
echo ========================================
echo   正在停止 ClawsJoy 服务...
echo ========================================
echo.

echo [1/2] 停止 Docker 后端...
wsl bash -c "cd /mnt/d/clawsjoy && docker-compose down"
echo ✅ Docker 服务已停止

echo [2/2] 停止 Chat API...
wsl bash -c "pkill -f chat_api_agent 2>/dev/null"
echo ✅ Chat API 已停止

echo.
echo ========================================
echo   ✅ 所有服务已停止
echo ========================================
pause
