@echo off
echo Starting Camera Monitoring Application...
echo.

cd /d "%~dp0"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Flask server...
echo Access the application at: http://localhost:5000
echo.

cd backend
python app.py

pause
