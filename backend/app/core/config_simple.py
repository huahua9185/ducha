"""
简化的配置文件，避免复杂依赖
"""
import secrets
from typing import List


class Settings:
    """简化的应用配置"""
    
    # 应用基本信息
    APP_NAME: str = "政府效能督查系统"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # JWT配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30天
    ALGORITHM: str = "HS256"
    
    # 服务器配置
    SERVER_NAME: str = "localhost"
    SERVER_HOST: str = "http://localhost"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost",
    ]
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ducha_db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # 安全配置
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
    PASSWORD_MIN_LENGTH: int = 8
    
    # 调试模式
    DEBUG: bool = False
    
    # 初始管理员
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    # 环境
    ENVIRONMENT: str = "development"


# 创建配置实例
settings = Settings()