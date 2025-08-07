from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta

from database.connection import get_db
from models.user import User
from auth.password import verify_password, get_password_hash
from auth.jwt_handler import create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()

# 请求模型
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

# 依赖函数：获取当前用户
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在（如果提供了邮箱）
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == user_data.username).first()
    print("user_data", user_data)
    print("user", user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误1",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误2",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户账户已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.post("/init-admin")
def init_admin_user(db: Session = Depends(get_db)):
    """初始化管理员用户（仅在开发环境使用）"""
    # 检查是否已存在管理员用户
    admin_user = db.query(User).filter(User.is_admin == True).first()
    if admin_user:
        return {"message": "管理员用户已存在"}
    
    # 创建管理员用户
    admin_password = get_password_hash("admin123")
    admin_user = User(
        username="admin",
        email="admin@temu-app.com",
        password_hash=admin_password,
        is_admin=True
    )
    
    db.add(admin_user)
    db.commit()
    
    return {"message": "管理员用户创建成功", "username": "admin", "password": "admin123"} 