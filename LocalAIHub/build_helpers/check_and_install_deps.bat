@echo off
REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo Python not found. Please install Python 3.10+ and ensure it's on PATH.
  pause
  exit /b 1
)
python --version

REM Create venv
if not exist venv (
  python -m venv venv
)

call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install backend deps
pip install -r backend\requirements.txt

REM Check for Ollama
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo Ollama not found on PATH. If you want Ollama support, install Ollama and ensure 'ollama' is on PATH.
) else (
  echo Ollama found.
)

REM Check for ComfyUI directory
if exist "C:\ComfyUI" (
  echo ComfyUI directory found at C:\ComfyUI
) else (
  echo ComfyUI not found at C:\ComfyUI. Set COMFYUI_DIR environment variable if installed elsewhere.
)

echo All done. To run backend:
echo call venv\Scripts\activate
echo python backend\main.py
pause
