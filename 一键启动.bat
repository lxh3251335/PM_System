@echo off
chcp 65001 >nul
title 冷库项目管理系统 - 一键启动

echo ====================================
echo   冷库项目管理系统 - 一键启动
echo ====================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] 检查Python环境...
python --version
echo.

echo [2/4] 进入后端目录...
cd /d "%~dp0backend"
if errorlevel 1 (
    echo [错误] 无法进入backend目录
    pause
    exit /b 1
)
echo.

echo [3/4] 检查依赖包...
if not exist "pm_system.db" (
    echo [提示] 首次运行，正在安装依赖并初始化数据库...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo.
    echo [提示] 初始化数据库...
    python init_data.py
    if errorlevel 1 (
        echo [错误] 数据库初始化失败
        pause
        exit /b 1
    )
)
echo.

echo [4/4] 启动后端服务...
echo.
echo ====================================
echo   后端服务启动中...
echo   API文档: http://localhost:8000/docs
echo   健康检查: http://localhost:8000/
echo ====================================
echo.
echo [提示] 请勿关闭此窗口！
echo [提示] 按 Ctrl+C 可以停止服务
echo.

:: 启动后端
start /b uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

:: 等待后端启动
echo [提示] 等待后端服务启动（5秒）...
timeout /t 5 /nobreak >nul

:: 打开前端页面
echo [提示] 打开前端页面...
start http://localhost:8000/docs
start "%~dp0demo\project-list.html"

echo.
echo ====================================
echo   启动完成！
echo ====================================
echo.
echo 前端地址: %~dp0demo\project-list.html
echo API文档: http://localhost:8000/docs
echo.
echo 按任意键停止服务...
pause >nul

:: 清理
taskkill /f /im python.exe /fi "WINDOWTITLE eq 冷库项目管理系统*" >nul 2>&1
echo 服务已停止
