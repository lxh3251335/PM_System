"""
用户管理 API（使用统一认证依赖）
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas import user as schemas
from ..auth_utils import get_current_user, require_admin, normalize_role
from ..password_utils import hash_password_bcrypt

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户列表（仅管理员）"""
    require_admin(current_user)
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/companies", response_model=List[str])
async def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取所有企业名称列表（仅管理员，用于筛选）"""
    require_admin(current_user)
    rows = db.query(User.company_name).filter(
        User.company_name.isnot(None),
        User.company_name != ""
    ).distinct().all()
    return [r[0] for r in rows]


@router.post("/", response_model=schemas.User, status_code=201)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建用户（仅管理员）"""
    require_admin(current_user)

    username = user.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="用户名不能为空")

    exists = db.query(User).filter(User.username == username).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")

    role = normalize_role(user.role)

    db_user = User(
        username=username,
        password_hash=hash_password_bcrypt(user.password),
        company_name=user.company_name or "",
        role=role,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新用户（启用/停用/角色/密码，仅管理员）"""
    require_admin(current_user)

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if db_user.id == current_user.id:
        if payload.is_active is False:
            raise HTTPException(status_code=400, detail="不能停用当前登录账号")
        if payload.role and normalize_role(payload.role) != "admin":
            raise HTTPException(status_code=400, detail="不能将当前登录账号降级为客户")

    if payload.company_name is not None:
        db_user.company_name = payload.company_name
    if payload.role is not None:
        db_user.role = normalize_role(payload.role)
    if payload.is_active is not None:
        db_user.is_active = payload.is_active
    if payload.password:
        db_user.password_hash = hash_password_bcrypt(payload.password)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除用户（仅管理员）"""
    require_admin(current_user)

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录账号")

    if db_user.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin", User.is_active == True).count()  # noqa: E712
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="系统至少保留一个启用状态的管理员")

    db.delete(db_user)
    db.commit()
    return {"message": "用户删除成功"}
