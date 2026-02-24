"""
认证 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user import LoginRequest, LoginResponse
from ..auth_utils import create_access_token, get_current_user
from ..password_utils import verify_password, needs_rehash, hash_password_bcrypt

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """用户名密码登录，返回 JWT Token"""
    username = payload.username.strip()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用，请联系管理员")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 旧 SHA256 密码自动迁移为 bcrypt
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password_bcrypt(payload.password)
        db.commit()

    token = create_access_token(user.id, user.username, user.role)
    return LoginResponse(
        id=user.id,
        username=user.username,
        company_name=user.company_name or "",
        role=user.role,
        is_active=user.is_active,
        access_token=token
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息（验证 Token 有效性）"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "company_name": current_user.company_name or "",
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
