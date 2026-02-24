"""
应用配置文件
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用设置"""
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./pm_system.db"
    
    # JWT配置（生产环境必须通过 .env 设置 SECRET_KEY）
    SECRET_KEY: str = "CHANGE-ME-IN-DOTENV"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # 应用信息
    APP_NAME: str = "冷库项目登记管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS配置（生产环境通过 .env 设置允许的域名）
    CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
