@echo off
REM Windows启动脚本

echo =========================================
echo 冷库项目登记管理系统 - 后端服务启动
echo =========================================

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.9+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖...
pip install -r requirements.txt

REM 检查环境变量
if not exist ".env" (
    echo 警告: .env 文件不存在，请根据 env.example 创建
    echo 复制 env.example 到 .env...
    copy env.example .env
    echo 请修改 .env 文件中的数据库配置！
    pause
    exit /b 1
)

echo 启动服务...
echo API文档: http://localhost:8000/docs
echo =========================================

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
