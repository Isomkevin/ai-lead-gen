@echo off
echo ==================================================
echo 🚀 Lead Generator - Localhost Setup
echo ==================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

echo ✅ Node.js found
node --version
echo.

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Install backend dependencies
echo 📦 Installing backend dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)

echo ✅ Backend dependencies installed
echo.

REM Check for .env file
if not exist .env (
    echo ⚠️  No .env file found!
    echo 📝 Creating .env template...
    copy env.example .env
    echo ✅ .env file created. Please add your GEMINI_API_KEY!
    echo    Get your key from: https://aistudio.google.com/app/apikey
    echo.
)

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend

if exist package.json (
    call npm install
    
    if errorlevel 1 (
        echo ❌ Failed to install frontend dependencies
        pause
        exit /b 1
    )
    
    echo ✅ Frontend dependencies installed
) else (
    echo ❌ package.json not found in frontend directory
    pause
    exit /b 1
)

cd ..

echo.
echo ==================================================
echo ✅ Setup Complete!
echo ==================================================
echo.
echo 📝 Next Steps:
echo.
echo 1. Add your GEMINI_API_KEY to the .env file
echo    (Edit .env in the project root)
echo.
echo 2. Start the backend API (open a new terminal):
echo    venv\Scripts\activate
echo    python api.py
echo.
echo 3. Start the frontend (open another terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open your browser:
echo    Frontend: http://localhost:3000
echo    API Docs: http://localhost:8000/docs
echo.
echo ==================================================
pause

