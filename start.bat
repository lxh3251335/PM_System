@echo off
chcp 65001 >nul
title PM System - Cold Storage Project Management
echo ==========================================
echo   Cold Storage Project Management System
echo ==========================================
echo.
echo Starting...
echo.

cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual env not found. Run first:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Server: http://localhost:8000
echo.
echo Accounts:
echo   Admin:    admin001 / admin@2024!
echo   Customer: customer001 / customer@2024!
echo.
echo Press Ctrl+C to stop.
echo ==========================================

start "" "http://localhost:8000/login.html"

venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause
