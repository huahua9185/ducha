#!/usr/bin/env python3
"""
政府效能督查系统启动脚本
使用简化配置，避免复杂依赖问题
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta, datetime
import uvicorn
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 简化配置
DATABASE_URL = "postgresql://postgres:password@localhost:5432/ducha_db"
SECRET_KEY = "your-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8小时

# 创建数据库引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="政府效能督查系统",
    description="政府效能督查管理平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 简化的认证函数
def authenticate_user_simple(db: Session, username: str, password: str):
    """简化的用户认证"""
    try:
        from app.services.auth_service import authenticate_user
        return authenticate_user(db, username, password)
    except ImportError:
        # 如果服务模块导入失败，使用直接SQL查询
        result = db.execute(
            "SELECT id, username, real_name, password_hash, is_active, is_superuser FROM \"user\" WHERE username = :username",
            {"username": username}
        ).fetchone()
        
        if result:
            # 简化的密码验证（生产环境需要使用bcrypt）
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            if pwd_context.verify(password, result[3]):
                return type('User', (), {
                    'id': result[0],
                    'username': result[1], 
                    'real_name': result[2],
                    'is_active': result[4],
                    'is_superuser': result[5]
                })()
        return None

# 简化的令牌生成
def create_simple_token(user_id: str) -> str:
    """简化的令牌生成"""
    try:
        from app.core.security import create_access_token
        return create_access_token(user_id, expires_delta=timedelta(hours=8))
    except ImportError:
        # 简化的令牌（生产环境需要使用JWT）
        import base64
        import json
        payload = {
            "sub": str(user_id),
            "exp": (datetime.utcnow() + timedelta(hours=8)).timestamp()
        }
        return base64.b64encode(json.dumps(payload).encode()).decode()

# 健康检查端点
@app.get("/api/v1/health")
@app.get("/health") 
def health_check():
    """系统健康检查"""
    try:
        # 测试数据库连接
        db = SessionLocal()
        db.execute("SELECT 1").fetchone()
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": {"status": db_status},
            "api": {"status": "healthy"}
        }
    }

# 登录端点
@app.post("/api/v1/auth/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """用户登录（OAuth2格式）"""
    user = authenticate_user_simple(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号已被禁用"
        )
    
    # 生成访问令牌
    access_token = create_simple_token(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "real_name": user.real_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser
        }
    }

# JSON格式登录端点
@app.post("/api/v1/auth/login-json")
def login_json(
    credentials: dict,
    db: Session = Depends(get_db)
):
    """用户登录（JSON格式）"""
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名和密码不能为空"
        )
    
    user = authenticate_user_simple(db, username, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号已被禁用"
        )
    
    access_token = create_simple_token(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "real_name": user.real_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser
        }
    }

# 根路径
@app.get("/")
def root():
    """系统信息"""
    return {
        "message": "政府效能督查系统",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health",
        "login_info": {
            "username": "admin",
            "password": "admin123",
            "oauth2_endpoint": "/api/v1/auth/login",
            "json_endpoint": "/api/v1/auth/login-json"
        }
    }

if __name__ == "__main__":
    print("🚀 启动政府效能督查系统...")
    print("=" * 50)
    print(f"📡 服务地址: http://localhost:8000")
    print(f"📖 API文档: http://localhost:8000/docs") 
    print(f"🏥 健康检查: http://localhost:8000/api/v1/health")
    print(f"🔑 登录信息: admin / admin123")
    print("=" * 50)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 系统已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)