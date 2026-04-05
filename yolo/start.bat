@echo off
echo Starting Fire Detection System...
echo.

cd /d "%~dp0"

echo Installing dependencies...
pip install flask flask-sqlalchemy flask-cors opencv-python ultralytics

echo.
echo Starting Flask server...
echo Access the application at: http://localhost:5000
echo.

python app.py

pause
