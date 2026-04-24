@echo off
cd /d "%~dp0"
call .\venv\Scripts\activate.bat
pip install -q -r requirements.txt 2>nul
python main.py --ahora
pause
