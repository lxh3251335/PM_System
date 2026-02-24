#!/bin/bash
# 启动脚本

echo "========================================="
echo "冷库项目登记管理系统 - 后端服务启动"
echo "========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.9+"
    exit 1
fi

# 检查依赖
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，请根据 env.example 创建"
    echo "复制 env.example 到 .env..."
    cp env.example .env
    echo "请修改 .env 文件中的数据库配置！"
    exit 1
fi

echo "启动服务..."
echo "API文档: http://localhost:8000/docs"
echo "========================================="

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
