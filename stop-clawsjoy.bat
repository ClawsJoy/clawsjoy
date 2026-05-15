@echo off
title ClawsJoy Shutdown
color 0C
echo ========================================
echo    Stopping all ClawsJoy services...
echo ========================================
echo.

echo [1/3] Stopping Chat API...
wsl bash -c "pkill -f chat_api_agent 2>/dev/null"
echo [OK] Chat API stopped
echo.

echo [2/3] Stopping Docker backend...
wsl bash -c "cd /mnt/d/clawsjoy && docker-compose down"
echo [OK] Docker services stopped
echo.

echo [3/3] Stopping Ollama (optional)...
wsl bash -c "pkill -f ollama 2>/dev/null"
echo [OK] Ollama stopped (if was running)
echo.

echo ========================================
echo    ALL SERVICES STOPPED
echo ========================================
pause
