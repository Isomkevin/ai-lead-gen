@echo off
echo ==================================================
echo 🚀 Starting Backend API Server
echo ==================================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found!
    echo    Run setup-localhost.bat first
    pause
    exit /b 1
)

REM Check for .env file
if not exist .env (
    echo ⚠️  .env file not found!
    echo    Please create .env file with GEMINI_API_KEY
    pause
    exit /b 1
)

echo ✅ Starting API server on http://localhost:8000
echo 📚 API Docs will be available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python api.py

