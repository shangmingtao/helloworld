"""
路由模块 - 用户登录、注册、注销
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from .auth import auth_service
from .database import UserModel
from .models import UserRegister, UserLogin, UserResponse, TokenResponse, MessageResponse

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """获取当前用户依赖"""
    token = credentials.credentials
    session = auth_service.validate_token(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌或令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """用户注册"""
    # 检查用户是否已存在
    existing_user = UserModel.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 密码加密
    hashed_password = auth_service.hash_password(user_data.password)
    
    # 创建用户
    success = UserModel.create_user(
        username=user_data.username,
        password=hashed_password,
        email=user_data.email
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户注册失败"
        )
    
    # 获取新创建的用户信息
    user = UserModel.get_user_by_username(user_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户创建成功但获取信息失败"
        )
    
    # 生成令牌
    token = auth_service.generate_token(user['id'], user['username'])
    
    user_response = UserResponse(
        id=user['id'],
        username=user['username'],
        email=user.get('email'),
        created_at=str(user['created_at']),
        is_active=bool(user['is_active'])
    )
    
    return TokenResponse(
        token=token,
        user=user_response,
        message="注册成功"
    )

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """用户登录"""
    # 密码加密
    hashed_password = auth_service.hash_password(user_data.password)
    
    # 验证用户
    user = UserModel.verify_user(user_data.username, hashed_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成令牌
    token = auth_service.generate_token(user['id'], user['username'])
    
    user_response = UserResponse(
        id=user['id'],
        username=user['username'],
        email=user.get('email'),
        created_at=str(user['created_at']),
        is_active=bool(user['is_active'])
    )
    
    return TokenResponse(
        token=token,
        user=user_response,
        message="登录成功"
    )

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """用户注销"""
    # 从请求头获取令牌
    # 注意：这里简化处理，实际中应该从依赖中获取令牌
    # 为了演示，我们假设能从某个地方获取令牌
    
    # 由于FastAPI的HTTPBearer设计，我们需要用另一种方式处理
    return MessageResponse(
        message="注销成功（请客户端删除令牌）",
        success=True
    )

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    user_id = current_user['user_id']
    
    # 从数据库重新获取最新用户信息
    # 这里简化处理，直接返回会话中的信息
    return UserResponse(
        id=user_id,
        username=current_user['username'],
        email=None,  # 可以从数据库获取
        created_at=str(current_user['created_at']),
        is_active=True
    )