@echo off
setlocal
cd /d %~dp0

echo 编译 ClawsJoy 客户端...
set WIN_CSC=%SystemRoot%\Microsoft.NET\Framework64\v4.0.30319\csc.exe
if not exist "%WIN_CSC%" set WIN_CSC=%SystemRoot%\Microsoft.NET\Framework\v4.0.30319\csc.exe

"%WIN_CSC%" /target:winexe /out:ClawsJoy.exe /win32icon:icon.ico ClawsJoy.cs

if exist ClawsJoy.exe (
    echo 编译成功: ClawsJoy.exe
) else (
    echo 编译失败，请安装 .NET Framework
)
pause
