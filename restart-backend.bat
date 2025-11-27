@echo off
echo ==================================================
echo 🔄 Restarting Backend Server
echo ==================================================
echo.

echo Stopping existing Python processes...
Get-Process python -ErrorAction SilentlyContinue | Stop-Process
timeout /t 2 /nobreak >nul

echo Starting backend server...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python api.py
) else (
    echo ⚠️  Virtual environment not found!
    echo    Run setup-localhost.bat first
    pause
)

