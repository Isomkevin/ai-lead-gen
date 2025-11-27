@echo off
echo ==================================================
echo 🎨 Starting Frontend Development Server
echo ==================================================
echo.

REM Check if in frontend directory
if not exist package.json (
    echo ⚠️  Not in frontend directory!
    echo    Changing to frontend directory...
    cd frontend
)

REM Check if node_modules exists
if not exist node_modules (
    echo ⚠️  Dependencies not installed!
    echo    Installing dependencies...
    call npm install
)

echo ✅ Starting frontend on http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

