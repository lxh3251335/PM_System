-- 阿里云 RDS MySQL 初始化脚本
-- 在 RDS 控制台创建数据库后执行

CREATE DATABASE IF NOT EXISTS pm_system
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 创建应用专用用户（可选，也可使用 RDS 主账号）
-- CREATE USER 'pm_admin'@'%' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
-- GRANT ALL PRIVILEGES ON pm_system.* TO 'pm_admin'@'%';
-- FLUSH PRIVILEGES;

-- 注意：表结构由 SQLAlchemy 的 Base.metadata.create_all() 自动创建
-- 首次启动应用后会自动建表和创建默认管理员账号
