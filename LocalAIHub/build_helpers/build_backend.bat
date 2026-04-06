@echo off
REM Build backend into single exe using PyInstaller
call venv\Scripts\activate

REM Install PyInstaller if missing
pip show pyinstaller >nul 2>nul
if %ERRORLEVEL% neq 0 (
  pip install pyinstaller
)

REM Create logs dir
if not exist backend\logs mkdir backend\logs

REM Build single-file exe
pyinstaller --onefile --name LocalAIHubBackend --add-data "backend;backend" backend\main.py

echo Build finished. Dist is in dist\LocalAIHubBackend.exe
pause
