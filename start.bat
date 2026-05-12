@echo off
REM Start the Flask web app for invoice planning in a new window
cd /d %~dp0
set FLASK_APP=app.py
set FLASK_ENV=development
start "Invoice Planner - Flask Server" python app.py
echo Flask server started in new window on http://localhost:5050
