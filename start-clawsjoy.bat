@echo off
title ClawsJoy All-in-One Startup
color 0A
echo ========================================
echo    ClawsJoy All-in-One Startup
echo ========================================
echo.

echo [1/5] Starting Docker backend...
wsl bash -c "cd /mnt/d/clawsjoy && docker-compose up -d"
echo [OK] Docker services started
echo.

echo [2/5] Starting Chat API...
wsl bash -c "cd /mnt/d/clawsjoy && pkill -f chat_api_agent 2>/dev/null; nohup python3 bin/chat_api_agent.py > /tmp/chat_api.log 2>&1 &"
timeout /t 2 /nobreak >nul
echo [OK] Chat API started on port 8101
echo.

echo [3/5] Ensuring Ollama is running...
wsl bash -c "pgrep -f 'ollama serve' || (export OLLAMA_HOST=0.0.0.0 && nohup ollama serve > /tmp/ollama.log 2>&1 &)"
echo [OK] Ollama is running
echo.

echo [4/5] Verifying services...
wsl bash -c "curl -s -X POST http://localhost:8101/api/agent -H 'Content-Type: application/json' -d '{\"text\":\"ping\"}' > /dev/null 2>&1"
if %errorlevel% equ 0 (
    echo [OK] Chat API verified
) else (
    echo [WARN] Chat API may need more time
)
echo.

echo [5/5] Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:8082/joymate/index.html

echo.
echo ========================================
echo    ALL SERVICES STARTED!
echo ========================================
echo.
echo    JoyMate Chat: http://localhost:8082/joymate/index.html
echo    Editor: http://localhost:8082/joymate/editor.html
echo    Library: http://localhost:8082/joymate/library.html
echo.
echo    API Endpoints:
echo    Chat API: http://localhost:8101/api/agent
echo.
echo ========================================
pause
