# 冷库项目管理系统 -- 部署指南

## 一、环境要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 服务器 | 1核2G | 2核4G |
| 系统 | CentOS 7+ / Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| Python | 3.9+ | 3.11 |
| 数据库 | SQLite（自带） | MySQL 8.0 |
| 端口 | 80 / 443（可选）/ 22 | 同左 |

---

## 二、快速部署（5 分钟）

### 2.1 上传代码到服务器

```bash
# 在本地执行（将整个项目上传到服务器）
scp -r PM_System/ root@YOUR_SERVER_IP:/opt/pm_system/
```

### 2.2 SSH 登录并执行部署

```bash
ssh root@YOUR_SERVER_IP

cd /opt/pm_system
chmod +x deploy/deploy.sh
bash deploy/deploy.sh
```

脚本会自动完成：安装依赖 → 创建虚拟环境 → 配置 Nginx → 启动服务。

### 2.3 验证

```bash
# 检查后端服务
curl http://127.0.0.1:8000/health
# 应返回 {"status":"ok"}

# 检查 Nginx
curl http://YOUR_SERVER_IP/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin001","password":"admin@2024!"}'
# 应返回包含 access_token 的 JSON
```

浏览器访问 `http://YOUR_SERVER_IP` 即可看到系统页面。

---

## 三、手动部署（详细步骤）

### 3.1 安装系统依赖

```bash
# Ubuntu
apt-get update && apt-get install -y python3 python3-pip python3-venv nginx

# CentOS
yum install -y python3 python3-pip nginx
```

### 3.2 部署代码

```bash
mkdir -p /opt/pm_system /var/log/pm_system /var/run/pm_system
# 将代码放入 /opt/pm_system/
```

### 3.3 Python 环境

```bash
cd /opt/pm_system
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install gunicorn
```

### 3.4 配置环境变量

```bash
cp deploy/env.production backend/.env
vi backend/.env
```

必须修改的项：
- `SECRET_KEY` —— 执行 `python3 -c "import secrets;print(secrets.token_urlsafe(48))"` 生成
- `CORS_ORIGINS` —— 改为你的实际域名或 IP
- `DATABASE_URL` —— 默认 SQLite，如用 MySQL 则取消注释修改

### 3.5 配置 Nginx

```bash
cp deploy/nginx.conf /etc/nginx/conf.d/pm_system.conf
# 编辑 server_name 为你的域名或 IP
vi /etc/nginx/conf.d/pm_system.conf

# 删除默认站点
rm -f /etc/nginx/sites-enabled/default

# 测试并重载
nginx -t && systemctl restart nginx
```

### 3.6 配置 Systemd 服务

```bash
cp deploy/pm_system.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pm_system
systemctl start pm_system
```

---

## 四、默认账号

系统首次启动会自动创建以下账号：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin001 | admin@2024! | 管理员 |
| customer001 | customer@2024! | 客户 |

**登录后请立即修改密码！**

---

## 五、日常运维

```bash
# 查看服务状态
systemctl status pm_system

# 重启后端
systemctl restart pm_system

# 查看错误日志
tail -f /var/log/pm_system/error.log

# 查看访问日志
tail -f /var/log/pm_system/access.log

# 重载 Nginx
nginx -t && systemctl reload nginx

# 查看数据库（SQLite）
cd /opt/pm_system/backend
sqlite3 pm_system.db ".tables"
```

---

## 六、升级操作

```bash
# 1. 备份数据库
cp /opt/pm_system/backend/pm_system.db /opt/pm_system/backend/pm_system.db.bak.$(date +%Y%m%d)

# 2. 上传新代码（覆盖旧文件，保留 .env 和 .db）
scp -r PM_System/backend/ root@YOUR_IP:/opt/pm_system/backend/
scp -r PM_System/demo/ root@YOUR_IP:/opt/pm_system/demo/

# 3. 安装新依赖（如有）
cd /opt/pm_system && source venv/bin/activate
pip install -r backend/requirements.txt

# 4. 重启服务
systemctl restart pm_system
```

---

## 七、切换到 MySQL

当数据量增大或需要多用户并发时，建议从 SQLite 切换到 MySQL：

```bash
# 1. 安装 MySQL
apt-get install -y mysql-server
# 或使用阿里云 RDS

# 2. 创建数据库
mysql -u root -p < /opt/pm_system/deploy/init_db.sql

# 3. 修改配置
vi /opt/pm_system/backend/.env
# 注释掉 SQLite 行，取消 MySQL 行的注释，填入连接信息

# 4. 修改 gunicorn workers（MySQL 支持多 worker）
vi /opt/pm_system/deploy/gunicorn.conf.py
# 将 workers = 1 改为 workers = 2 或 4

# 5. 重启服务（会自动建表）
systemctl restart pm_system
```

---

## 八、HTTPS 配置

### 8.1 申请 SSL 证书

- 阿里云免费证书：控制台 → SSL证书 → 免费证书
- Let's Encrypt：`certbot --nginx -d your-domain.com`

### 8.2 切换 Nginx 配置

编辑 `/etc/nginx/conf.d/pm_system.conf`：
1. 注释掉"方案A"（HTTP）
2. 取消"方案B"（HTTPS）的注释
3. 修改 `server_name` 和 SSL 证书路径
4. `nginx -t && systemctl reload nginx`

同时更新 `backend/.env` 的 `CORS_ORIGINS` 为 HTTPS 地址。

---

## 九、安全清单

- [ ] 修改 `SECRET_KEY` 为随机字符串
- [ ] 修改默认账号密码
- [ ] 安全组仅开放 80/443/22 端口，不暴露 8000
- [ ] 如用 MySQL，设置 RDS 白名单仅允许 ECS IP
- [ ] 启用 HTTPS
- [ ] 定期备份数据库
