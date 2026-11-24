@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe python -m venv .venv
call .venv\Scripts\activate.bat
if not exist .env copy .env.example .env
findstr /C:"YOUR_MYSQL_PASSWORD" .env >nul
if %errorlevel%==0 (
  echo Edit backend\.env and set your MySQL password before running the API.
  pause
  exit /b 1
)
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
