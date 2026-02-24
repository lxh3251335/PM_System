"""
Gunicorn 配置文件
用于生产环境部署 FastAPI 应用
"""

bind = "127.0.0.1:8000"

# Worker 配置
# SQLite 模式：必须用 1 个 worker（SQLite 不支持并发写入）
# MySQL 模式：可改为 2-4
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 100

timeout = 120
graceful_timeout = 30
keepalive = 5

accesslog = "/var/log/pm_system/access.log"
errorlog = "/var/log/pm_system/error.log"
loglevel = "info"

pidfile = "/var/run/pm_system/gunicorn.pid"
daemon = False

preload_app = True
