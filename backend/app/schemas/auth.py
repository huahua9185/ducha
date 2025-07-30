from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """访问令牌响应"""
    access_token: str
    token_type: str
    expires_in: int


class TokenPayload(BaseModel):
    """令牌载荷"""
    sub: Optional[str] = None
    type: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: "User"


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    email: str


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str
    new_password: str


# 避免循环导入
from app.schemas.user import User
LoginResponse.model_rebuild()