#!/bin/bash
# ===========================================
# 冷库项目管理系统 - 云服务器部署脚本
# 适用于 CentOS 7/8 或 Ubuntu 20.04+
# ===========================================

set -e

APP_DIR="/opt/pm_system"
LOG_DIR="/var/log/pm_system"
PID_DIR="/var/run/pm_system"

echo "=== 1. 安装系统依赖 ==="
if command -v yum &>/dev/null; then
    yum install -y python3 python3-pip nginx git
elif command -v apt-get &>/dev/null; then
    apt-get update && apt-get install -y python3 python3-pip python3-venv nginx git
fi

echo "=== 2. 创建目录 ==="
mkdir -p $APP_DIR $LOG_DIR $PID_DIR
chown www-data:www-data $LOG_DIR $PID_DIR 2>/dev/null || true

echo "=== 3. 部署代码 ==="
echo "[提示] 请确保代码已复制到 $APP_DIR/"
echo "  方式1: scp -r PM_System/* root@YOUR_IP:$APP_DIR/"
echo "  方式2: git clone https://your-repo.git $APP_DIR"

echo "=== 4. 创建 Python 虚拟环境 ==="
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

echo "=== 5. 安装 Python 依赖 ==="
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install gunicorn

echo "=== 6. 配置环境变量 ==="
if [ ! -f backend/.env ]; then
    cp deploy/env.production backend/.env
    # 自动生成 JWT 密钥
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
    sed -i "s|CHANGE_THIS_TO_A_RANDOM_STRING|$SECRET|g" backend/.env
    echo ""
    echo "[重要] 请编辑 backend/.env 确认配置："
    echo "  vi $APP_DIR/backend/.env"
    echo ""
fi

echo "=== 7. 配置 Nginx ==="
cp deploy/nginx.conf /etc/nginx/conf.d/pm_system.conf
# 删除默认站点（避免冲突）
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
nginx -t && systemctl reload nginx

echo "=== 8. 配置 Systemd 服务 ==="
cp deploy/pm_system.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pm_system
systemctl start pm_system

echo "=== 9. 验证 ==="
sleep 3
systemctl status pm_system --no-pager
curl -s http://127.0.0.1:8000/health

echo ""
echo "==========================================="
echo "  部署完成！"
echo "==========================================="
echo ""
echo "默认账号："
echo "  管理员: admin001 / admin@2024!"
echo "  客户:   customer001 / customer@2024!"
echo ""
echo "常用命令："
echo "  查看状态:  systemctl status pm_system"
echo "  重启服务:  systemctl restart pm_system"
echo "  查看日志:  tail -f $LOG_DIR/error.log"
echo "  编辑配置:  vi $APP_DIR/backend/.env"
echo ""
echo "请务必修改默认密码！"
echo "==========================================="
