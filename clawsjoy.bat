@echo off
title ClawsJoy AI 助手
echo 启动 ClawsJoy 后端...
wsl -d Ubuntu -- cd /mnt/d/clawsjoy && ./start.sh
timeout /t 3 /nobreak >nul
echo 打开 ClawsJoy...
start http://localhost:5002
