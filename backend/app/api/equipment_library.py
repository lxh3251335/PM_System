"""
标准设备库 API
重构：三级动态结构 (Category -> Brand -> Model)
使用统一 JWT 认证
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.equipment_library import EquipmentBrand, EquipmentModel, EquipmentCategory
from ..models.user import User
from ..schemas import equipment_library as schemas
from ..auth_utils import get_current_user, require_admin

router = APIRouter()


# ========== 1. 设备类型 (Category) API ==========

@router.get("/categories", response_model=List[schemas.EquipmentCategory])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有设备类型"""
    return db.query(EquipmentCategory).offset(skip).limit(limit).all()


@router.post("/categories", response_model=schemas.EquipmentCategory, status_code=201)
async def create_category(
    category: schemas.EquipmentCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员新建设备类型"""
    require_admin(current_user)
    if db.query(EquipmentCategory).filter(
        (EquipmentCategory.code == category.code) | (EquipmentCategory.name == category.name)
    ).first():
        raise HTTPException(status_code=400, detail="类型编码或名称已存在")
    
    db_cat = EquipmentCategory(**category.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@router.put("/categories/{cat_id}", response_model=schemas.EquipmentCategory)
async def update_category(
    cat_id: int,
    cat_update: schemas.EquipmentCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新设备类型"""
    require_admin(current_user)
    db_cat = db.query(EquipmentCategory).filter(EquipmentCategory.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="类型不存在")
    
    for k, v in cat_update.model_dump(exclude_unset=True).items():
        setattr(db_cat, k, v)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@router.delete("/categories/{cat_id}")
async def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除设备类型（级联删除品牌和型号）"""
    require_admin(current_user)
    db_cat = db.query(EquipmentCategory).filter(EquipmentCategory.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="类型不存在")
    db.delete(db_cat)
    db.commit()
    return {"message": "删除成功"}


# ========== 2. 设备品牌 (Brand) API ==========

@router.get("/brands", response_model=List[schemas.EquipmentBrand])
async def get_brands(
    category_id: int = Query(None, description="按类型ID筛选"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取品牌列表"""
    q = db.query(EquipmentBrand)
    if category_id:
        q = q.filter(EquipmentBrand.category_id == category_id)
    return q.offset(skip).limit(limit).all()


@router.post("/brands", response_model=schemas.EquipmentBrand, status_code=201)
async def create_brand(
    brand: schemas.EquipmentBrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建品牌（登录用户均可）"""
    if not db.query(EquipmentCategory).filter(EquipmentCategory.id == brand.category_id).first():
        raise HTTPException(status_code=404, detail="关联的设备类型不存在")

    db_brand = EquipmentBrand(**brand.model_dump())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


@router.put("/brands/{brand_id}", response_model=schemas.EquipmentBrand)
async def update_brand(
    brand_id: int,
    brand_update: schemas.EquipmentBrandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新品牌（包括更新属性模板）"""
    db_brand = db.query(EquipmentBrand).filter(EquipmentBrand.id == brand_id).first()
    if not db_brand:
        raise HTTPException(status_code=404, detail="品牌不存在")
    
    for k, v in brand_update.model_dump(exclude_unset=True).items():
        setattr(db_brand, k, v)
    db.commit()
    db.refresh(db_brand)
    return db_brand


@router.delete("/brands/{brand_id}")
async def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除品牌"""
    db_brand = db.query(EquipmentBrand).filter(EquipmentBrand.id == brand_id).first()
    if not db_brand:
        raise HTTPException(status_code=404, detail="品牌不存在")
    db.delete(db_brand)
    db.commit()
    return {"message": "删除成功"}


# ========== 3. 设备型号 (Model) API ==========

@router.get("/models", response_model=List[schemas.EquipmentModelWithBrand])
async def get_models(
    brand_id: int = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取型号列表"""
    q = db.query(EquipmentModel)
    if brand_id:
        q = q.filter(EquipmentModel.brand_id == brand_id)
    return q.offset(skip).limit(limit).all()


@router.post("/models", response_model=schemas.EquipmentModel, status_code=201)
async def create_model(
    model: schemas.EquipmentModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建型号"""
    brand = db.query(EquipmentBrand).filter(EquipmentBrand.id == model.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="品牌不存在")
    
    if db.query(EquipmentModel).filter(
        EquipmentModel.brand_id == model.brand_id,
        EquipmentModel.model_name == model.model_name
    ).first():
        raise HTTPException(status_code=400, detail="该品牌下型号名称已存在")

    db_model = EquipmentModel(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.put("/models/{model_id}", response_model=schemas.EquipmentModel)
async def update_model(
    model_id: int,
    model_update: schemas.EquipmentModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新型号数据"""
    db_model = db.query(EquipmentModel).filter(EquipmentModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="型号不存在")
    
    for k, v in model_update.model_dump(exclude_unset=True).items():
        setattr(db_model, k, v)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除型号"""
    db_model = db.query(EquipmentModel).filter(EquipmentModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="型号不存在")
    db.delete(db_model)
    db.commit()
    return {"message": "删除成功"}
