#!/usr/bin/env python3
"""
简化的启动脚本
只包含认证和核心功能，避免复杂依赖
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import uvicorn

# 基础导入
from app.db.session import SessionLocal
from app.services.auth_service import authenticate_user, update_last_login
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User

# 创建FastAPI应用
app = FastAPI(
    title="政府效能督查系统",
    description="核心认证服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
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

# 健康检查端点
@app.get("/api/v1/health")
@app.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "政府效能督查系统运行正常",
        "version": "1.0.0"
    }

# OAuth2登录端点
@app.post("/api/v1/auth/login")
def login_oauth2(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2表单登录"""
    user = authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号已被禁用"
        )
    
    # 生成令牌
    access_token = create_access_token(user.id, expires_delta=timedelta(hours=8))
    refresh_token = create_refresh_token(user.id, expires_delta=timedelta(days=30))
    
    # 更新登录时间
    update_last_login(db, user_id=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 28800,  # 8小时
        "user": {
            "id": str(user.id),
            "username": user.username,
            "real_name": user.real_name,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser
        }
    }

# JSON登录端点（方便前端调用）
@app.post("/api/v1/auth/login-json")
def login_json(
    credentials: dict,
    db: Session = Depends(get_db)
):
    """JSON格式登录"""
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名和密码不能为空"
        )
    
    user = authenticate_user(db, username=username, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号已被禁用"
        )
    
    # 生成令牌
    access_token = create_access_token(user.id, expires_delta=timedelta(hours=8))
    refresh_token = create_refresh_token(user.id, expires_delta=timedelta(days=30))
    
    # 更新登录时间
    update_last_login(db, user_id=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 28800,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "real_name": user.real_name,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser
        }
    }

# 基础信息端点
@app.get("/")
def root():
    return {
        "message": "政府效能督查系统API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "login_oauth2": "/api/v1/auth/login",
            "login_json": "/api/v1/auth/login-json",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    print("🚀 启动政府效能督查系统...")
    print("📡 健康检查: http://localhost:8000/api/v1/health")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔑 登录信息: admin/admin123")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )