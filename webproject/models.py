"""
Pydantic数据模型
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    """用户注册请求模型"""
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str
    password: str

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: Optional[str] = None
    created_at: str
    is_active: bool
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """令牌响应模型"""
    token: str
    user: UserResponse
    message: str

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str
    success: bool