@echo off
echo Testing Camera Monitoring Application Setup...
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Checking virtual environment...
if not exist "venv" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Checking dependencies...
pip list | findstr "Flask opencv-python"

echo.
echo Checking directory structure...
if exist "backend\app.py" (
    echo [OK] backend/app.py found
) else (
    echo [ERROR] backend/app.py not found
)

if exist "templates\bind.html" (
    echo [OK] templates/bind.html found
) else (
    echo [ERROR] templates/bind.html not found
)

if exist "templates\monitor.html" (
    echo [OK] templates/monitor.html found
) else (
    echo [ERROR] templates/monitor.html not found
)

if exist "static\css\bind.css" (
    echo [OK] static/css/bind.css found
) else (
    echo [ERROR] static/css/bind.css not found
)

if exist "static\css\monitor.css" (
    echo [OK] static/css/monitor.css found
) else (
    echo [ERROR] static/css/monitor.css not found
)

if exist "static\js\bind.js" (
    echo [OK] static/js/bind.js found
) else (
    echo [ERROR] static/js/bind.js not found
)

if exist "static\js\monitor.js" (
    echo [OK] static/js/monitor.js found
) else (
    echo [ERROR] static/js/monitor.js not found
)

echo.
echo Setup check complete!
echo.
echo To start the application, run: start.bat
pause
