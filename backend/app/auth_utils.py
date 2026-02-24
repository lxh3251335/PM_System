"""
JWT 认证工具模块
提供统一的 token 生成/验证 和 get_current_user 依赖
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models.user import User


def create_access_token(user_id: int, username: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="无效或已过期的Token，请重新登录")


def normalize_role(role: Optional[str]) -> str:
    raw = (role or "customer").lower()
    if raw == "factory":
        return "admin"
    if raw == "user":
        return "customer"
    return raw if raw in ("admin", "customer") else "customer"


async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    x_username: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    统一的用户认证依赖。
    优先使用 Authorization Bearer token (JWT)；
    兼容旧的 X-User-Role / X-Username header 方式。
    """
    # --- 方式1: JWT ---
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token内容异常")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="账号已停用，请联系管理员")
        return user

    # --- 方式2: 兼容旧 Header ---
    from urllib.parse import unquote
    username = unquote((x_username or "").strip())
    if username:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="登录用户不存在")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="账号已停用")
        return user

    raise HTTPException(status_code=401, detail="缺少登录凭证，请先登录")


def require_admin(user: User) -> User:
    """校验当前用户是否为管理员"""
    role = normalize_role(user.role)
    if role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可执行此操作")
    return user


def check_project_permission(db: Session, project_id: int, user: User):
    """
    校验用户对项目的访问权限。
    管理员可访问所有项目，客户只能访问自己创建的项目。
    返回 Project 对象。
    """
    from .models.project import Project
    query = db.query(Project).filter(Project.id == project_id)
    role = normalize_role(user.role)
    if role != "admin":
        query = query.filter(Project.created_by == user.id)
    project = query.first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限访问")
    return project
