from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, field_validator
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    """应用配置"""
    
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
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 数据库配置
    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: Optional[str] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return v
        # 返回默认数据库URL
        return "postgresql://postgres:password@localhost:5432/ducha_db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # 邮件配置
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_FROM_NAME", mode="before")
    @classmethod
    def get_project_name(cls, v: Optional[str]) -> str:
        if not v:
            return "政府效能督查系统"
        return v

    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'
    ]
    UPLOAD_DIR: str = "./uploads"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # 安全配置
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SYMBOLS: bool = False
    
    # 验证码配置
    CAPTCHA_ENABLED: bool = True
    CAPTCHA_LENGTH: int = 4
    CAPTCHA_EXPIRE_MINUTES: int = 5
    
    # 限流配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # 秒
    
    # 系统集成配置
    OA_SYSTEM_URL: Optional[str] = None
    OA_SYSTEM_KEY: Optional[str] = None
    HR_SYSTEM_URL: Optional[str] = None
    HR_SYSTEM_KEY: Optional[str] = None
    FINANCE_SYSTEM_URL: Optional[str] = None
    FINANCE_SYSTEM_KEY: Optional[str] = None
    
    # 消息推送配置
    WECHAT_ENABLED: bool = False
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    SMS_ENABLED: bool = False
    SMS_API_KEY: Optional[str] = None
    SMS_API_SECRET: Optional[str] = None
    
    # 调试模式
    DEBUG: bool = False
    
    # 测试模式
    TESTING: bool = False
    
    # 初始管理员
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    # 环境
    ENVIRONMENT: str = "development"
    
    # 监控配置
    PROMETHEUS_ENABLED: bool = False
    PROMETHEUS_PORT: int = 9090
    
    # 备份配置
    BACKUP_ENABLED: bool = True
    BACKUP_DIR: str = "./backups"
    BACKUP_KEEP_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


# 创建配置实例
settings = Settings()

# 配置文档
TAGS_METADATA = [
    {
        "name": "认证",
        "description": "用户认证相关接口",
    },
    {
        "name": "用户管理",
        "description": "用户和权限管理接口",
    },
    {
        "name": "督办管理", 
        "description": "督办事项管理接口",
    },
    {
        "name": "工作流",
        "description": "工作流程管理接口",
    },
    {
        "name": "系统管理",
        "description": "系统配置和管理接口",
    },
    {
        "name": "文件管理",
        "description": "文件上传和管理接口",
    },
    {
        "name": "统计分析",
        "description": "数据统计和分析接口",
    },
    {
        "name": "消息通知",
        "description": "消息通知相关接口",
    },
]