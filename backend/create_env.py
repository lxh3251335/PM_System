"""
创建正确编码的.env文件
"""

env_content = """# Database Configuration
# 开发环境：使用SQLite（无需安装MySQL，快速启动）
DATABASE_URL=sqlite:///./pm_system.db

# 生产环境：切换到MySQL（取消下面的注释，注释掉上面的SQLite）
# DATABASE_URL=mysql+pymysql://pm_user:pm_password123@localhost:3306/pm_system

# 生产环境：或使用PostgreSQL
# DATABASE_URL=postgresql://pm_user:pm_password123@localhost:5432/pm_system

# JWT Secret
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=冷库项目登记管理系统
APP_VERSION=1.0.0
DEBUG=True

# CORS - 允许本地开发和文件访问
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8000","http://127.0.0.1:8000","http://localhost:5500","http://127.0.0.1:5500","null"]
"""

# 使用UTF-8编码写入
with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print(".env file created successfully (UTF-8 encoding)")
