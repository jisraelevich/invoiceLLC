@echo off
REM Stop any Python Flask processes (Windows only)
taskkill /F /IM python.exe /T >nul 2>&1
echo Flask processes terminated.

REM Kill process on port 5050
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5050') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo Port 5050 cleared.

timeout /t 2 /nobreak
