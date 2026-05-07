@echo off
title ClawsJoy 启动器
color 0A
echo ========================================
echo   正在启动 ClawsJoy 服务...
echo ========================================
echo.

echo [1/3] 启动 Docker 后端...
wsl bash -c "cd /mnt/d/clawsjoy && docker-compose up -d"
if %errorlevel% neq 0 (
    echo ❌ Docker 启动失败
    pause
    exit /b 1
)
echo ✅ Docker 服务已启动

echo [2/3] 启动 Chat API...
wsl bash -c "cd /mnt/d/clawsjoy && pkill -f chat_api_agent 2>/dev/null; nohup python3 bin/chat_api_agent.py > /tmp/chat_api.log 2>&1 &"
echo ✅ Chat API 已启动

echo [3/3] 等待服务就绪...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   ✅ 所有服务已启动！
echo ========================================
echo.
echo   📱 访问地址:
echo      聊天: http://localhost:8082/joymate/index.html
echo      编辑器: http://localhost:8082/joymate/editor.html
echo      资料库: http://localhost:8082/joymate/library.html
echo.
echo   🔧 管理命令:
echo      wsl docker-compose ps
echo      wsl pm2 status
echo.
echo ========================================
echo   按任意键关闭此窗口（服务继续运行）
pause >nul
