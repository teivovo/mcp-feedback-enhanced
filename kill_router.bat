@echo off
echo Killing all router instances...

REM Find and kill all node processes running telegram-router.js
for /f "tokens=2" %%i in ('netstat -ano ^| findstr :8080') do (
    echo Killing process %%i on port 8080
    taskkill /F /PID %%i
)

echo Done.
pause
